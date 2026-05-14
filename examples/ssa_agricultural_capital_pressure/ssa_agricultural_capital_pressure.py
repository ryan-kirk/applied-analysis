from csv import DictReader
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

from applied_analysis.contextual_events import (
    build_context_windows,
    load_context_events,
    match_events_to_windows,
)
from applied_analysis.thresholds import detect_threshold_runs, format_duration


AGRICULTURE_DATA_PATH = (
    REPO_ROOT
    / "examples"
    / "agriculture_system_pressure_africa"
    / "data"
    / "sub_saharan_africa_food_import_pressure.csv"
)
CAPITAL_COST_PATH = BASE_DIR / "data" / "ssa_capital_cost_proxy.csv"
EVENTS_PATH = BASE_DIR / "data" / "contextual_events.csv"
CHART_PATH = BASE_DIR / "ssa_agricultural_capital_pressure.png"
SUMMARY_PATH = BASE_DIR / "ssa_agricultural_capital_pressure_summary.txt"

REGION_NAME = "Sub-Saharan Africa"
QUESTION = "When imported-food pressure crosses an attention threshold, which contextual events and capital-cost conditions help explain what was happening around that period?"
WINDOW_PREFIX = "Pressure window"
THRESHOLD = 0.15
EVENT_LOOKBACK_YEARS = 1


def load_agriculture_series(path):
    with path.open(newline="", encoding="utf-8") as file:
        return [
            {
                "year": int(row["year"]),
                "agriculture_value_added_usd": float(row["agriculture_value_added_usd"]),
                "merchandise_imports_usd": float(row["merchandise_imports_usd"]),
                "food_import_share_percent": float(row["food_import_share_percent"]),
                "population": int(row["population"]),
            }
            for row in DictReader(file)
        ]


def load_capital_cost_series(path):
    with path.open(newline="", encoding="utf-8") as file:
        return {
            int(row["year"]): {
                "nigeria_lending_rate": float(row["nigeria_lending_rate"]) if row["nigeria_lending_rate"] else None,
                "south_africa_lending_rate": float(row["south_africa_lending_rate"]),
                "kenya_lending_rate": float(row["kenya_lending_rate"]),
                "ssa_capital_cost_proxy": float(row["ssa_capital_cost_proxy"]),
            }
            for row in DictReader(file)
        }


def average(values):
    if not values:
        return 0.0
    return sum(values) / len(values)


def percent_change(start, end):
    if start == 0:
        return 0.0
    return ((end - start) / start) * 100


def format_billions(value):
    return f"${value / 1_000_000_000:.1f}B"


def format_rate(value):
    return f"{value:.1f}%"


def repo_relative_path(path):
    return path.relative_to(REPO_ROOT).as_posix()


def join_series(agriculture_series, capital_cost_by_year):
    joined = []
    for point in agriculture_series:
        capital_context = capital_cost_by_year.get(point["year"])
        if capital_context is None:
            continue

        estimated_food_imports = (
            point["merchandise_imports_usd"] * point["food_import_share_percent"] / 100
        )
        imported_food_share = estimated_food_imports / (
            point["agriculture_value_added_usd"] + estimated_food_imports
        )

        joined.append(
            {
                **point,
                **capital_context,
                "estimated_food_imports_usd": estimated_food_imports,
                "imported_food_share_of_supply": imported_food_share,
            }
        )

    return joined


def describe_window(window, matches):
    relevant = [item for item in matches if item.window_name == window.name]
    if not relevant:
        return f"{window.name} ({window.start}-{window.end}) had no curated events in the one-year lead or during-window scope."

    event_text = "; ".join(
        f"{item.event.year} {item.event.event_name} ({item.timing})"
        for item in relevant
    )
    return f"{window.name} ({window.start}-{window.end}) aligned with {event_text}."


def summarize(series, events):
    years = [point["year"] for point in series]
    imported_share = [point["imported_food_share_of_supply"] for point in series]
    capital_costs = [point["ssa_capital_cost_proxy"] for point in series]
    crossings, runs = detect_threshold_runs(list(zip(years, imported_share)), THRESHOLD)
    windows = build_context_windows(runs, prefix=WINDOW_PREFIX)
    matches = match_events_to_windows(events, windows, years_before=EVENT_LOOKBACK_YEARS)
    peak_index = max(range(len(series)), key=lambda index: imported_share[index])
    capital_peak_index = max(range(len(series)), key=lambda index: capital_costs[index])

    window_summaries = []
    for window in windows:
        window_points = [point for point in series if window.start <= point["year"] <= window.end]
        pre_points = [
            point for point in series if window.start - EVENT_LOOKBACK_YEARS <= point["year"] < window.start
        ]
        window_summaries.append(
            {
                "window": window,
                "average_imported_share": average(
                    [point["imported_food_share_of_supply"] for point in window_points]
                ),
                "average_capital_cost": average(
                    [point["ssa_capital_cost_proxy"] for point in window_points]
                ),
                "pre_window_capital_cost": average(
                    [point["ssa_capital_cost_proxy"] for point in pre_points]
                ),
                "events": [item for item in matches if item.window_name == window.name],
            }
        )

    return {
        "start_year": years[0],
        "end_year": years[-1],
        "threshold": THRESHOLD,
        "crossings": crossings,
        "windows": windows,
        "window_summaries": window_summaries,
        "event_matches": matches,
        "peak_imported_share": imported_share[peak_index],
        "peak_imported_share_year": years[peak_index],
        "peak_capital_cost": capital_costs[capital_peak_index],
        "peak_capital_cost_year": years[capital_peak_index],
        "latest_imported_share": imported_share[-1],
        "latest_capital_cost": capital_costs[-1],
        "capital_cost_change_percent": percent_change(capital_costs[0], capital_costs[-1]),
        "imported_share_change_percent": percent_change(imported_share[0], imported_share[-1]),
        "population_start": series[0]["population"],
        "population_end": series[-1]["population"],
        "population_change_percent": percent_change(series[0]["population"], series[-1]["population"]),
        "agriculture_start": series[0]["agriculture_value_added_usd"],
        "agriculture_end": series[-1]["agriculture_value_added_usd"],
        "imports_start": series[0]["estimated_food_imports_usd"],
        "imports_end": series[-1]["estimated_food_imports_usd"],
    }


def interpret(summary):
    if not summary["windows"]:
        return (
            f"The imported-food-share proxy never crossed the {summary['threshold']:.0%} threshold in this sample, "
            "so there are no pressure windows to contextualize with events."
        )

    first_window = summary["window_summaries"][0]
    last_window = summary["window_summaries"][-1]
    first_shift = first_window["average_capital_cost"] - first_window["pre_window_capital_cost"]
    event_count = len(summary["event_matches"])

    return (
        f"The imported-food-share proxy crossed into two sustained pressure windows: "
        f"{summary['windows'][0].start}-{summary['windows'][0].end} and "
        f"{summary['windows'][1].start}-{summary['windows'][1].end}. "
        f"A total of {event_count} curated events fall either in the year before or during those windows, which helps explain what was happening around the pressure episodes without claiming those events caused the threshold crossing. "
        f"Capital costs were already elevated entering the first window and averaged {format_rate(first_window['average_capital_cost'])} during it, "
        f"{first_shift:+.1f} percentage points versus the one-year lead period. "
        f"By the second window, imported-food pressure stayed above threshold even as the capital-cost proxy eased from its {summary['peak_capital_cost_year']} peak, which suggests the signal reflects a wider system context rather than a single financing variable. "
        f"The latest reading is below threshold, but imported-food share remains above its 2000 level while the capital-cost proxy has moved back up from its 2021 low."
    )


def build_report(summary, interpretation, chart_path=None, summary_path=None):
    lines = [
        "Applied Analysis - Event Context Windows",
        "----------------------------------------",
        f"Question: {QUESTION}",
        f"Region: {REGION_NAME}",
        f"Time range: {summary['start_year']} to {summary['end_year']}",
        f"Threshold signal: Imported food share of available supply proxy above {summary['threshold']:.0%}",
        (
            f"Agriculture value added: {format_billions(summary['agriculture_start'])} -> "
            f"{format_billions(summary['agriculture_end'])}"
        ),
        (
            f"Estimated food imports: {format_billions(summary['imports_start'])} -> "
            f"{format_billions(summary['imports_end'])}"
        ),
        (
            f"Population context: {summary['population_start'] / 1_000_000:.0f}M -> "
            f"{summary['population_end'] / 1_000_000:.0f}M ({summary['population_change_percent']:+.1f}%)"
        ),
        (
            f"Imported-food-share change: {summary['imported_share_change_percent']:+.1f}% from the first to latest year"
        ),
        (
            f"Capital-cost proxy change: {summary['capital_cost_change_percent']:+.1f}% from the first to latest year"
        ),
        f"Peak imported-food share: {summary['peak_imported_share']:.1%} in {summary['peak_imported_share_year']}",
        f"Peak capital-cost proxy: {format_rate(summary['peak_capital_cost'])} in {summary['peak_capital_cost_year']}",
        f"Latest imported-food share: {summary['latest_imported_share']:.1%}",
        f"Latest capital-cost proxy: {format_rate(summary['latest_capital_cost'])}",
        "",
        "Pressure windows:",
    ]

    for item in summary["window_summaries"]:
        window = item["window"]
        lines.append(
            (
                f"- {window.name}: {window.start}-{window.end} ({format_duration(window.duration)}) | "
                f"avg imported share {item['average_imported_share']:.1%} | "
                f"avg capital cost {format_rate(item['average_capital_cost'])}"
            )
        )

    lines.extend(["", "Contextual events:"])
    for window in summary["windows"]:
        lines.append(f"- {describe_window(window, summary['event_matches'])}")

    lines.extend(
        [
            "",
            "What to notice:",
            interpretation,
            "",
            "Source note:",
            (
                "The imported-food data come from the existing local World Bank regional extract for Sub-Saharan Africa. "
                "Estimated food imports are recalculated as merchandise imports multiplied by the food-import share, and the threshold signal is estimated food imports / (agriculture value added + estimated food imports)."
            ),
            (
                "The capital-cost proxy is a simple annual average of World Bank lending interest-rate series for Nigeria, South Africa, and Kenya. "
                "That is a transparent regional financing proxy, not a complete measure of agricultural borrowing costs across Sub-Saharan Africa."
            ),
            (
                "Events are a small curated context set. Their timing may help interpretation, but the chart and summary do not prove causation."
            ),
        ]
    )

    if chart_path or summary_path:
        lines.extend(["", "Artifacts:"])

    if chart_path:
        lines.append(f"Chart: {chart_path}")

    if summary_path:
        lines.append(f"Summary: {summary_path}")

    return "\n".join(lines)


def save_chart(series, summary, path):
    years = [point["year"] for point in series]
    agriculture = [point["agriculture_value_added_usd"] / 1_000_000_000 for point in series]
    imports = [point["estimated_food_imports_usd"] / 1_000_000_000 for point in series]
    imported_share = [point["imported_food_share_of_supply"] * 100 for point in series]
    capital_costs = [point["ssa_capital_cost_proxy"] for point in series]
    threshold_percent = summary["threshold"] * 100

    fig, (top_ax, middle_ax, bottom_ax) = plt.subplots(
        3,
        1,
        figsize=(11, 9),
        sharex=True,
        height_ratios=[1.05, 1.2, 0.95],
    )

    top_ax.plot(years, agriculture, marker="o", linewidth=2.3, color="#2f6b3b", label="Agriculture value added")
    top_ax.plot(years, imports, marker="o", linewidth=2.3, color="#c46b2c", label="Estimated food imports")
    top_ax.set_title("SSA Agricultural Capital Pressure")
    top_ax.set_ylabel("USD (billions)")
    top_ax.grid(axis="y", alpha=0.25)
    top_ax.legend(frameon=False, loc="upper left")

    for window in summary["windows"]:
        middle_ax.axvspan(window.start, window.end, color="#f3d8c0", alpha=0.45)
        bottom_ax.axvspan(window.start, window.end, color="#f3d8c0", alpha=0.45)

    middle_ax.plot(years, imported_share, marker="o", linewidth=2.4, color="#204a87")
    middle_ax.axhline(threshold_percent, color="#aa2e25", linestyle="--", linewidth=1.8)
    middle_ax.set_ylabel("Imported share (%)")
    middle_ax.grid(axis="y", alpha=0.25)

    used_event_years = set()
    for index, match in enumerate(summary["event_matches"]):
        event_year = match.event.year
        event_value = next(
            point["imported_food_share_of_supply"] * 100 for point in series if point["year"] == event_year
        )
        offset = 1.0 + (index % 3) * 1.5
        if event_year in used_event_years:
            offset += 1.0
        used_event_years.add(event_year)
        middle_ax.axvline(event_year, color="#666666", alpha=0.18, linewidth=1)
        middle_ax.scatter([event_year], [event_value], color="#aa2e25", s=35, zorder=3)
        middle_ax.annotate(
            f"{event_year} {match.event.event_name}",
            xy=(event_year, event_value),
            xytext=(event_year + 0.25, event_value + offset),
            fontsize=7.5,
            va="bottom",
            arrowprops={"arrowstyle": "-", "color": "#555555", "lw": 0.8},
        )

    middle_ax.text(
        years[0] + 0.2,
        threshold_percent + 0.35,
        f"Threshold: {threshold_percent:.0f}%",
        color="#aa2e25",
        fontsize=9,
    )

    bottom_ax.plot(years, capital_costs, marker="o", linewidth=2.3, color="#6b4ea0")
    bottom_ax.set_xlabel("Year")
    bottom_ax.set_ylabel("Capital cost proxy (%)")
    bottom_ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_summary(report, path):
    path.write_text(report + "\n", encoding="utf-8")


def main():
    agriculture_series = load_agriculture_series(AGRICULTURE_DATA_PATH)
    capital_cost_by_year = load_capital_cost_series(CAPITAL_COST_PATH)
    events = load_context_events(EVENTS_PATH)
    series = join_series(agriculture_series, capital_cost_by_year)
    summary = summarize(series, events)
    interpretation = interpret(summary)

    save_chart(series, summary, CHART_PATH)
    summary_report = build_report(summary, interpretation)
    save_summary(summary_report, SUMMARY_PATH)

    console_report = build_report(
        summary,
        interpretation,
        chart_path=repo_relative_path(CHART_PATH),
        summary_path=repo_relative_path(SUMMARY_PATH),
    )
    print(console_report)


if __name__ == "__main__":
    main()