from csv import DictReader, DictWriter
from datetime import datetime
import os
from pathlib import Path
import sys
from tempfile import gettempdir

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(gettempdir()) / "applied-analysis-matplotlib"),
)
try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    raise SystemExit(
        "Matplotlib is required. Run: python3 -m pip install -r requirements.txt"
    )


BASE_DIR = Path(__file__).parent
REPO_ROOT = BASE_DIR.parents[1]
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from applied_analysis.contextual_events import ContextEvent, build_context_windows, match_events_to_windows
from applied_analysis.signal_comparison import (
    classify_trend_direction,
    compare_signal_directions,
    compare_trend_consistency,
)
from applied_analysis.thresholds import detect_threshold_runs, format_duration


TITLE = "Can AI Infrastructure Keep Up?"
QUESTION = "Can AI infrastructure keep up with growing AI demand?"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
SIGNALS_PATH = DATA_DIR / "ai_infrastructure_signals.csv"
EVENTS_PATH = DATA_DIR / "ai_infrastructure_events.csv"
CHART_PATH = OUTPUT_DIR / "ai_compute_constraints.png"
SUMMARY_PATH = OUTPUT_DIR / "ai_compute_constraints_summary.csv"

DEMAND_SIGNAL = "ai_demand_index"
SUPPLY_SIGNALS = [
    "gpu_supply_index",
    "hbm_supply_index",
    "storage_supply_index",
    "power_capacity_index",
]
SIGNAL_LABELS = {
    "ai_demand_index": "AI demand index",
    "gpu_supply_index": "GPU supply index",
    "hbm_supply_index": "HBM supply index",
    "storage_supply_index": "Storage supply index",
    "power_capacity_index": "Power capacity index",
}
SIGNAL_COLORS = {
    "ai_demand_index": "#111827",
    "gpu_supply_index": "#0f766e",
    "hbm_supply_index": "#9333ea",
    "storage_supply_index": "#b45309",
    "power_capacity_index": "#be123c",
}

PRESSURE_GAP_THRESHOLD = 0.25
BOTTLENECK_GAP_THRESHOLD = 0.50
CONSISTENCY_THRESHOLD = 0.60


def load_signals(path):
    with path.open(newline="", encoding="utf-8") as file:
        return [
            {
                "year": int(row["year"]),
                "signal_name": row["signal_name"].strip(),
                "category": row["category"].strip(),
                "value": float(row["value"]),
                "unit": row["unit"].strip(),
                "source": row["source"].strip(),
            }
            for row in DictReader(file)
        ]


def load_events(path):
    with path.open(newline="", encoding="utf-8") as file:
        return [
            {
                "event_date": datetime.strptime(row["event_date"], "%Y-%m-%d").date(),
                "event_name": row["event_name"].strip(),
                "event_type": row["event_type"].strip(),
                "description": row["description"].strip(),
                "source": row["source"].strip(),
            }
            for row in DictReader(file)
        ]


def percent_change(start, end):
    if start == 0:
        return 0.0
    return (end - start) / start


def average(values):
    if not values:
        return 0.0
    return sum(values) / len(values)


def repo_relative_path(path):
    return path.relative_to(REPO_ROOT).as_posix()


def year_fraction(event_date):
    start_of_year = datetime(event_date.year, 1, 1).date()
    end_of_year = datetime(event_date.year + 1, 1, 1).date()
    elapsed = (event_date - start_of_year).days
    duration = (end_of_year - start_of_year).days
    return event_date.year + (elapsed / duration)


def format_percent(value):
    return f"{value:.1%}"


def format_score(value):
    return f"{value:.2f}"


def pairwise_consistency_score(reference_growth, comparison_growth):
    if abs(reference_growth) <= 1e-9:
        return 1.0
    gap = abs(reference_growth - comparison_growth)
    return max(0.0, 1.0 - min(gap / abs(reference_growth), 1.0))


def build_signal_lookup(rows):
    by_signal = {}
    for row in rows:
        by_signal.setdefault(row["signal_name"], []).append(row)

    for signal_rows in by_signal.values():
        signal_rows.sort(key=lambda item: item["year"])

    return by_signal


def compute_growth_by_signal(signal_rows):
    growth_by_signal = {}
    for signal_name, rows in signal_rows.items():
        yearly_growth = {}
        for previous, current in zip(rows[:-1], rows[1:]):
            yearly_growth[current["year"]] = percent_change(previous["value"], current["value"])
        growth_by_signal[signal_name] = yearly_growth
    return growth_by_signal


def annotate_events(ax, events, y_position, *, show_labels=False):
    for event in events:
        position = year_fraction(event["event_date"])
        ax.axvline(position, color="#7c6f64", linewidth=1.0, alpha=0.16)
        if show_labels:
            ax.text(
                position,
                y_position,
                event["event_name"],
                rotation=90,
                va="top",
                ha="right",
                fontsize=7,
                color="#57534e",
            )


def build_event_layout(events):
    sorted_events = sorted(events, key=lambda item: item["event_date"])
    upper_levels = [0.84, 0.72, 0.60]
    lower_levels = [0.18, 0.30, 0.42]
    laid_out = []
    cluster_index = 0
    previous_position = None

    for index, event in enumerate(sorted_events):
        position = year_fraction(event["event_date"])
        if previous_position is None or abs(position - previous_position) > 0.33:
            cluster_index = 0
        else:
            cluster_index += 1

        place_above = index % 2 == 0
        levels = upper_levels if place_above else lower_levels
        y_value = levels[cluster_index % len(levels)]
        x_offset = ((cluster_index % 3) - 1) * 0.06 if cluster_index else 0.0

        laid_out.append(
            {
                **event,
                "position": position,
                "label_x": position + x_offset,
                "label_y": y_value,
                "label_above": place_above,
            }
        )
        previous_position = position

    return laid_out


def highlight_windows(ax, windows, color, alpha=0.08):
    for window in windows:
        ax.axvspan(window.start - 0.45, window.end + 0.45, color=color, alpha=alpha)


def summarize(signal_rows, events):
    years = [row["year"] for row in signal_rows[DEMAND_SIGNAL]]
    growth_by_signal = compute_growth_by_signal(signal_rows)

    directions = {
        signal_name: classify_trend_direction([row["value"] for row in rows])
        for signal_name, rows in signal_rows.items()
    }
    average_supply_series = [
        average([
            signal_rows[signal_name][index]["value"]
            for signal_name in SUPPLY_SIGNALS
        ])
        for index in range(len(years))
    ]
    demand_vs_supply = compare_signal_directions(
        directions[DEMAND_SIGNAL],
        classify_trend_direction(average_supply_series),
        "AI demand",
        "Aggregate infrastructure supply",
    )

    yearly_summary = []
    for year in years[1:]:
        growth_rates = {signal_name: growth_by_signal[signal_name][year] for signal_name in signal_rows}
        consistency = compare_trend_consistency(
            growth_rates,
            demand_signal=DEMAND_SIGNAL,
            pressure_gap=PRESSURE_GAP_THRESHOLD,
            bottleneck_gap=BOTTLENECK_GAP_THRESHOLD,
        )
        resource_gaps = {
            signal_name: growth_rates[DEMAND_SIGNAL] - growth_rates[signal_name]
            for signal_name in SUPPLY_SIGNALS
        }
        resource_consistency_scores = {
            signal_name: pairwise_consistency_score(growth_rates[DEMAND_SIGNAL], growth_rates[signal_name])
            for signal_name in SUPPLY_SIGNALS
        }
        strongest_constraint = consistency["strongest_constraint"]
        max_gap = max(resource_gaps.values())

        yearly_summary.append(
            {
                "year": year,
                "demand_growth": growth_rates[DEMAND_SIGNAL],
                "gpu_gap": resource_gaps["gpu_supply_index"],
                "memory_gap": resource_gaps["hbm_supply_index"],
                "storage_gap": resource_gaps["storage_supply_index"],
                "power_gap": resource_gaps["power_capacity_index"],
                "gpu_consistency_score": resource_consistency_scores["gpu_supply_index"],
                "memory_consistency_score": resource_consistency_scores["hbm_supply_index"],
                "storage_consistency_score": resource_consistency_scores["storage_supply_index"],
                "power_consistency_score": resource_consistency_scores["power_capacity_index"],
                "max_growth_gap": max_gap,
                "strongest_constraint": strongest_constraint or "none",
                "consistency_score": consistency["consistency_score"],
                "classification": consistency["classification"],
            }
        )

    pressure_windows = build_context_windows(
        detect_threshold_runs(
            [(row["year"], row["max_growth_gap"]) for row in yearly_summary],
            PRESSURE_GAP_THRESHOLD,
        )[1],
        prefix="Resource pressure window",
    )
    bottleneck_windows = build_context_windows(
        detect_threshold_runs(
            [(row["year"], row["max_growth_gap"]) for row in yearly_summary],
            BOTTLENECK_GAP_THRESHOLD,
        )[1],
        prefix="Potential constraint window",
    )
    divergence_windows = build_context_windows(
        detect_threshold_runs(
            [(row["year"], 1 - row["consistency_score"]) for row in yearly_summary],
            1 - CONSISTENCY_THRESHOLD,
        )[1],
        prefix="System divergence window",
    )
    context_events = [
        ContextEvent(
            year=event["event_date"].year,
            event_type=event["event_type"],
            event_name=event["event_name"],
            description=event["description"],
            source_url=event["source"],
        )
        for event in events
    ]
    divergence_event_matches = match_events_to_windows(
        context_events,
        divergence_windows,
        years_before=1,
        years_after=0,
    )

    return {
        "years": years,
        "signal_rows": signal_rows,
        "directions": directions,
        "demand_vs_supply": demand_vs_supply,
        "yearly_summary": yearly_summary,
        "pressure_windows": pressure_windows,
        "bottleneck_windows": bottleneck_windows,
        "divergence_windows": divergence_windows,
        "divergence_event_matches": divergence_event_matches,
        "events": events,
    }


def interpret(summary):
    demand_direction = summary["directions"][DEMAND_SIGNAL]
    supply_relationship = summary["demand_vs_supply"]
    yearly_summary = summary["yearly_summary"]
    strongest_constraint_counts = {}
    for row in yearly_summary:
        strongest_constraint_counts[row["strongest_constraint"]] = (
            strongest_constraint_counts.get(row["strongest_constraint"], 0) + 1
        )
    dominant_constraint = max(strongest_constraint_counts, key=strongest_constraint_counts.get)
    divergence_windows = summary["divergence_windows"]
    pressure_windows = summary["pressure_windows"]
    event_text = "; ".join(
        f"{item.event.year} {item.event.event_name} ({item.timing})"
        for item in summary["divergence_event_matches"]
    ) or "No divergence-window event matches were found."

    return (
        f"AI demand is {demand_direction}, and aggregate infrastructure supply is also {supply_relationship['signal_b_direction']}, so the broad directional comparison suggests agreement rather than outright conflict. "
        f"But the more useful signal comes from consistency analysis: {len(pressure_windows)} resource pressure window(s) and {len(divergence_windows)} system divergence window(s) appear once demand growth starts pulling away from slower-moving infrastructure layers. "
        f"Across the yearly comparisons, the most common strongest constraint is {SIGNAL_LABELS.get(dominant_constraint, dominant_constraint)}. "
        f"That means the system does not look supply-free; it looks directionally aligned but unevenly scaled. Relevant event context around divergence windows: {event_text}"
    )


def build_report(summary, interpretation):
    pressure_windows = ", ".join(
        f"{window.name} {window.start}-{window.end} ({format_duration(window.duration)})"
        for window in summary["pressure_windows"]
    ) or "none"
    bottleneck_windows = ", ".join(
        f"{window.name} {window.start}-{window.end} ({format_duration(window.duration)})"
        for window in summary["bottleneck_windows"]
    ) or "none"
    divergence_windows = ", ".join(
        f"{window.name} {window.start}-{window.end} ({format_duration(window.duration)})"
        for window in summary["divergence_windows"]
    ) or "none"
    latest = summary["yearly_summary"][-1]

    lines = [
        TITLE,
        "-" * len(TITLE),
        f"Question: {QUESTION}",
        f"Demand vs infrastructure direction: {summary['demand_vs_supply']['relationship']}",
        f"Latest consistency score ({latest['year']}): {format_score(latest['consistency_score'])}",
        f"Latest strongest constraint: {latest['strongest_constraint']}",
        f"Resource pressure windows: {pressure_windows}",
        f"Potential constraint windows: {bottleneck_windows}",
        f"System divergence windows: {divergence_windows}",
        "",
        "Interpretation:",
        interpretation,
        "",
        f"Chart output: {repo_relative_path(CHART_PATH)}",
        f"Summary output: {repo_relative_path(SUMMARY_PATH)}",
    ]
    return "\n".join(lines)


def write_summary_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = DictWriter(
            file,
            fieldnames=[
                "year",
                "demand_growth",
                "gpu_gap",
                "memory_gap",
                "storage_gap",
                "power_gap",
                "gpu_consistency_score",
                "memory_consistency_score",
                "storage_consistency_score",
                "power_consistency_score",
                "max_growth_gap",
                "strongest_constraint",
                "consistency_score",
                "classification",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def build_chart(summary, path):
    years = summary["years"]
    signal_rows = summary["signal_rows"]
    events = summary["events"]
    yearly_summary = summary["yearly_summary"]
    event_layout = build_event_layout(events)

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), sharex=False)
    fig.suptitle(TITLE, fontsize=14, y=0.98)
    demand_ax = axes[0][0]
    gap_ax = axes[0][1]
    consistency_ax = axes[1][0]
    event_ax = axes[1][1]

    for signal_name in [DEMAND_SIGNAL] + SUPPLY_SIGNALS:
        demand_ax.plot(
            years,
            [row["value"] for row in signal_rows[signal_name]],
            marker="o",
            linewidth=2.4 if signal_name == DEMAND_SIGNAL else 2.0,
            color=SIGNAL_COLORS[signal_name],
            label=SIGNAL_LABELS[signal_name],
        )
    demand_ax.set_title("AI Demand vs. Infrastructure Supply")
    demand_ax.set_ylabel("Index (2020 = 100)")
    demand_ax.grid(axis="y", alpha=0.25)
    demand_ax.legend(frameon=False, fontsize=8)
    annotate_events(demand_ax, events, demand_ax.get_ylim()[1] * 0.98, show_labels=True)

    growth_years = [row["year"] for row in yearly_summary]
    gap_ax.plot(growth_years, [row["gpu_gap"] for row in yearly_summary], marker="o", color=SIGNAL_COLORS["gpu_supply_index"], label="Demand - GPU growth")
    gap_ax.plot(growth_years, [row["memory_gap"] for row in yearly_summary], marker="o", color=SIGNAL_COLORS["hbm_supply_index"], label="Demand - HBM growth")
    gap_ax.plot(growth_years, [row["storage_gap"] for row in yearly_summary], marker="o", color=SIGNAL_COLORS["storage_supply_index"], label="Demand - storage growth")
    gap_ax.plot(growth_years, [row["power_gap"] for row in yearly_summary], marker="o", color=SIGNAL_COLORS["power_capacity_index"], label="Demand - power growth")
    highlight_windows(gap_ax, summary["pressure_windows"], "#f59e0b", alpha=0.08)
    highlight_windows(gap_ax, summary["bottleneck_windows"], "#dc2626", alpha=0.08)
    gap_ax.axhline(PRESSURE_GAP_THRESHOLD, color="#b45309", linestyle="--", alpha=0.7)
    gap_ax.axhline(BOTTLENECK_GAP_THRESHOLD, color="#be123c", linestyle=":", alpha=0.8)
    gap_ax.text(growth_years[-1] + 0.08, PRESSURE_GAP_THRESHOLD, "Pressure > 25 pts", color="#b45309", va="bottom", ha="left", fontsize=8)
    gap_ax.text(growth_years[-1] + 0.08, BOTTLENECK_GAP_THRESHOLD, "Potential constraint > 50 pts", color="#be123c", va="bottom", ha="left", fontsize=8)
    gap_ax.set_title("Growth Gap Analysis")
    gap_ax.set_ylabel("Demand growth minus resource growth")
    gap_ax.grid(axis="y", alpha=0.25)
    gap_ax.legend(frameon=False, fontsize=8, loc="upper left")

    consistency_scores = [row["consistency_score"] for row in yearly_summary]
    consistency_ax.plot(
        growth_years,
        consistency_scores,
        marker="o",
        linewidth=2.8,
        color="#111827",
        label="System-wide consistency",
    )
    consistency_ax.plot(
        growth_years,
        [row["gpu_consistency_score" ] for row in yearly_summary],
        marker="o",
        linewidth=1.8,
        color=SIGNAL_COLORS["gpu_supply_index"],
        label="GPU vs demand",
    )
    consistency_ax.plot(
        growth_years,
        [row["memory_consistency_score"] for row in yearly_summary],
        marker="o",
        linewidth=1.8,
        color=SIGNAL_COLORS["hbm_supply_index"],
        label="HBM vs demand",
    )
    consistency_ax.plot(
        growth_years,
        [row["storage_consistency_score"] for row in yearly_summary],
        marker="o",
        linewidth=1.8,
        color=SIGNAL_COLORS["storage_supply_index"],
        label="Storage vs demand",
    )
    consistency_ax.plot(
        growth_years,
        [row["power_consistency_score"] for row in yearly_summary],
        marker="o",
        linewidth=2.2,
        color=SIGNAL_COLORS["power_capacity_index"],
        label="Power vs demand",
    )
    highlight_windows(consistency_ax, summary["divergence_windows"], "#1d4ed8", alpha=0.08)
    consistency_ax.axhline(CONSISTENCY_THRESHOLD, color="#1d4ed8", linestyle="--", alpha=0.7)
    consistency_ax.text(growth_years[-1] + 0.08, CONSISTENCY_THRESHOLD, "Divergence < 0.60", color="#1d4ed8", va="bottom", ha="left", fontsize=8)
    for row in yearly_summary:
        if row["strongest_constraint"] != "none":
            consistency_ax.text(
                row["year"],
                row["consistency_score"] - 0.05,
                SIGNAL_LABELS[row["strongest_constraint"]].replace(" index", ""),
                fontsize=7,
                ha="center",
                color="#57534e",
            )
    consistency_ax.set_ylim(0.0, 1.05)
    consistency_ax.set_title("Trend Consistency Scores by Resource")
    consistency_ax.set_ylabel("Score")
    consistency_ax.grid(axis="y", alpha=0.25)
    consistency_ax.legend(frameon=False, fontsize=8, loc="upper left")

    event_ax.set_title("Infrastructure Event Context")
    event_ax.set_xlim(years[0] - 0.2, years[-1] + 0.4)
    event_ax.set_ylim(0, 1)
    event_ax.set_yticks([])
    event_ax.grid(axis="x", alpha=0.18)
    event_ax.hlines(0.5, years[0], years[-1], color="#d6d3d1", linewidth=1.0)
    for event in event_layout:
        event_ax.scatter(event["position"], 0.5, color="#0f4c5c", s=26)
        event_ax.plot([event["position"], event["label_x"]], [0.5, event["label_y"]], color="#7c6f64", linewidth=1.0)
        event_ax.text(
            event["label_x"],
            event["label_y"],
            event["event_name"],
            ha="center",
            va="bottom" if event["label_above"] else "top",
            fontsize=8,
        )

    for ax in (gap_ax, consistency_ax):
        ax.set_xticks(growth_years)
        ax.set_xlim(growth_years[0] - 0.1, growth_years[-1] + 0.4)
        ax.set_xlabel("Year")

    demand_ax.set_xticks(years)
    demand_ax.set_xlabel("Year")
    event_ax.set_xticks(years)
    event_ax.set_xlabel("Year")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    signals = load_signals(SIGNALS_PATH)
    events = load_events(EVENTS_PATH)
    signal_rows = build_signal_lookup(signals)
    summary = summarize(signal_rows, events)
    interpretation = interpret(summary)

    write_summary_csv(summary["yearly_summary"], SUMMARY_PATH)
    build_chart(summary, CHART_PATH)
    print(build_report(summary, interpretation))


if __name__ == "__main__":
    main()