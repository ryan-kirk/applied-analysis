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

from applied_analysis.thresholds import detect_threshold_runs, format_duration


DATA_PATH = BASE_DIR / "data" / "sub_saharan_africa_food_import_pressure.csv"
CHART_PATH = BASE_DIR / "agriculture_system_pressure_africa.png"
SUMMARY_PATH = BASE_DIR / "agriculture_system_pressure_africa_summary.txt"
REGION_NAME = "Sub-Saharan Africa"
QUESTION = "When does imported food become a large enough share of the Sub-Saharan African food system to merit closer attention?"
PRODUCTION_NAME = "Agriculture value added"
IMPORT_NAME = "Estimated food imports"
SHARE_NAME = "Imported food share of available supply proxy"
POPULATION_NAME = "Population"
THRESHOLD = 0.15


def load_series(path):
    with path.open(newline="", encoding="utf-8") as file:
        return [
            {
                "year": int(row["year"]),
                "agriculture_value_added_usd": float(row["agriculture_value_added_usd"]),
                "merchandise_imports_usd": float(row["merchandise_imports_usd"]),
                "food_import_share_percent": float(row["food_import_share_percent"]),
                "food_imports_usd": float(row["food_imports_usd"]),
                "imported_food_share_of_supply": float(row["imported_food_share_of_supply"]),
                "population": int(row["population"]),
            }
            for row in DictReader(file)
        ]


def percent_change(start, end):
    if start == 0:
        return 0.0
    return ((end - start) / start) * 100


def average(values):
    if not values:
        return 0.0
    return sum(values) / len(values)


def crossing_text(crossings):
    if not crossings:
        return "The imported-share proxy did not cross the threshold in this sample."

    parts = []
    for crossing in crossings:
        movement = "rose above" if crossing.crossed_above else "fell back below"
        parts.append(f"{crossing.position} ({movement} {THRESHOLD:.0%} at {crossing.value:.1%})")
    return "; ".join(parts)


def summarize(series):
    years = [point["year"] for point in series]
    production = [point["agriculture_value_added_usd"] for point in series]
    imports = [point["food_imports_usd"] for point in series]
    imported_share = [point["imported_food_share_of_supply"] for point in series]
    population = [point["population"] for point in series]
    crossings, runs = detect_threshold_runs(list(zip(years, imported_share)), THRESHOLD)
    peak_index = max(range(len(series)), key=lambda index: imported_share[index])

    first_upward_crossing = next((crossing for crossing in crossings if crossing.crossed_above), None)
    pre_window = []
    during_window = []

    if first_upward_crossing:
        pre_window = [
            point for point in series if first_upward_crossing.position - 3 <= point["year"] < first_upward_crossing.position
        ]
        during_window = [
            point for point in series if first_upward_crossing.position <= point["year"] <= runs[0].end
        ]

    total_above_threshold_years = sum(run.duration for run in runs)

    return {
        "start_year": years[0],
        "end_year": years[-1],
        "production_start": production[0],
        "production_end": production[-1],
        "imports_start": imports[0],
        "imports_end": imports[-1],
        "population_start": population[0],
        "population_end": population[-1],
        "production_change_percent": percent_change(production[0], production[-1]),
        "imports_change_percent": percent_change(imports[0], imports[-1]),
        "population_change_percent": percent_change(population[0], population[-1]),
        "latest_share": imported_share[-1],
        "peak_year": years[peak_index],
        "peak_share": imported_share[peak_index],
        "threshold": THRESHOLD,
        "crossings": crossings,
        "runs": runs,
        "crossing_text": crossing_text(crossings),
        "total_above_threshold_years": total_above_threshold_years,
        "pre_crossing_average_share": average([point["imported_food_share_of_supply"] for point in pre_window]),
        "during_crossing_average_share": average([point["imported_food_share_of_supply"] for point in during_window]),
        "pre_crossing_average_imports": average([point["food_imports_usd"] for point in pre_window]),
        "during_crossing_average_imports": average([point["food_imports_usd"] for point in during_window]),
        "pre_crossing_average_production": average([point["agriculture_value_added_usd"] for point in pre_window]),
        "during_crossing_average_production": average([point["agriculture_value_added_usd"] for point in during_window]),
        "first_upward_crossing_year": first_upward_crossing.position if first_upward_crossing else None,
        "first_run_end_year": runs[0].end if runs else None,
    }


def format_billions(value):
    return f"${value / 1_000_000_000:.1f}B"


def interpret(summary):
    if not summary["runs"]:
        return (
            f"The imported-food-share proxy stayed below the {summary['threshold']:.0%} threshold throughout the sample. "
            "In this regional view, imports remained a smaller share of available food supply than the chosen alert level."
        )

    run_descriptions = ", ".join(
        f"{run.start}-{run.end} ({format_duration(run.duration)})" for run in summary["runs"]
    )

    return (
        f"The imported-food-share proxy first rose above the {summary['threshold']:.0%} threshold in "
        f"{summary['first_upward_crossing_year']} and spent {format_duration(summary['total_above_threshold_years'])} "
        f"above that level across the sample. Above-threshold stretches occurred in {run_descriptions}. "
        f"Before the first crossing, the proxy averaged {summary['pre_crossing_average_share']:.1%}; during the first "
        f"above-threshold stretch it averaged {summary['during_crossing_average_share']:.1%}. Over the full 2000-2024 "
        f"window, agriculture value added rose from {format_billions(summary['production_start'])} to "
        f"{format_billions(summary['production_end'])}, estimated food imports rose from "
        f"{format_billions(summary['imports_start'])} to {format_billions(summary['imports_end'])}, and the regional "
        f"population rose from {summary['population_start'] / 1_000_000:.0f}M to {summary['population_end'] / 1_000_000:.0f}M."
    )


def build_report(summary, interpretation, chart_path=None, summary_path=None):
    lines = [
        "Applied Analysis - Threshold Detection",
        "----------------------------------------",
        f"Question: {QUESTION}",
        f"Region: {REGION_NAME}",
        f"Time range: {summary['start_year']} to {summary['end_year']}",
        f"Signal A: {PRODUCTION_NAME}",
        (
            f"  {format_billions(summary['production_start'])} -> {format_billions(summary['production_end'])} "
            f"({summary['production_change_percent']:+.1f}%)"
        ),
        f"Signal B: {IMPORT_NAME}",
        (
            f"  {format_billions(summary['imports_start'])} -> {format_billions(summary['imports_end'])} "
            f"({summary['imports_change_percent']:+.1f}%)"
        ),
        (
            f"Threshold signal: {SHARE_NAME} above {summary['threshold']:.0%}"
        ),
        f"Crossings: {summary['crossing_text']}",
        f"Total years above threshold: {summary['total_above_threshold_years']}",
        f"Peak imported share: {summary['peak_share']:.1%} in {summary['peak_year']}",
        f"Latest imported share: {summary['latest_share']:.1%}",
        (
            f"Population context: {summary['population_start'] / 1_000_000:.0f}M -> "
            f"{summary['population_end'] / 1_000_000:.0f}M ({summary['population_change_percent']:+.1f}%)"
        ),
        "",
        "What changed before and after the first crossing:",
        (
            f"Imported share average: {summary['pre_crossing_average_share']:.1%} before -> "
            f"{summary['during_crossing_average_share']:.1%} during the first above-threshold stretch"
        ),
        (
            f"Estimated food imports average: {format_billions(summary['pre_crossing_average_imports'])} before -> "
            f"{format_billions(summary['during_crossing_average_imports'])} during"
        ),
        (
            f"Agriculture value added average: {format_billions(summary['pre_crossing_average_production'])} before -> "
            f"{format_billions(summary['during_crossing_average_production'])} during"
        ),
        "",
        "What to notice:",
        interpretation,
        "",
        "Source note:",
        (
            "This example uses a local extract of World Bank regional indicators for Sub-Saharan Africa: "
            "agriculture, forestry, and fishing value added (current US$), merchandise imports (current US$), "
            "food imports (% of merchandise imports), and total population. Estimated food imports are calculated "
            "as merchandise imports multiplied by the food-import share. The threshold signal uses an imported-food "
            "share proxy: food imports / (agriculture value added + food imports)."
        ),
        (
            "Interpretation is descriptive, not causal. The threshold is transparent and easy to change if a different "
            "attention level is more useful."
        ),
    ]

    if chart_path or summary_path:
        lines.extend(["", "Artifacts:"])

    if chart_path:
        lines.append(f"Chart: {chart_path}")

    if summary_path:
        lines.append(f"Summary: {summary_path}")

    return "\n".join(lines)


def save_chart(series, summary, path):
    years = [point["year"] for point in series]
    production = [point["agriculture_value_added_usd"] / 1_000_000_000 for point in series]
    imports = [point["food_imports_usd"] / 1_000_000_000 for point in series]
    imported_share = [point["imported_food_share_of_supply"] * 100 for point in series]
    population = [point["population"] / 1_000_000 for point in series]
    threshold_percent = summary["threshold"] * 100

    fig, (top_ax, bottom_ax) = plt.subplots(2, 1, figsize=(10, 7), sharex=True, height_ratios=[1.15, 1])
    top_ax_right = top_ax.twinx()

    top_ax.plot(years, production, marker="o", linewidth=2.4, color="#2f6b3b", label=PRODUCTION_NAME)
    top_ax.plot(years, imports, marker="o", linewidth=2.4, color="#c46b2c", label=IMPORT_NAME)
    top_ax_right.plot(
        years,
        population,
        linestyle=":",
        linewidth=2.2,
        color="#6b4ea0",
        label=POPULATION_NAME,
    )
    top_ax.set_title("Sub-Saharan Africa Agriculture System Pressure")
    top_ax.set_ylabel("Current USD (billions)")
    top_ax_right.set_ylabel("Population (millions)")
    top_ax.grid(axis="y", alpha=0.25)
    top_handles, top_labels = top_ax.get_legend_handles_labels()
    right_handles, right_labels = top_ax_right.get_legend_handles_labels()
    top_ax.legend(top_handles + right_handles, top_labels + right_labels, frameon=False, loc="upper left")

    for run in summary["runs"]:
        bottom_ax.axvspan(run.start, run.end, color="#f3d8c0", alpha=0.45)

    bottom_ax.plot(years, imported_share, marker="o", linewidth=2.4, color="#204a87")
    bottom_ax.axhline(threshold_percent, color="#aa2e25", linestyle="--", linewidth=1.8)
    bottom_ax.set_xlabel("Year")
    bottom_ax.set_ylabel("Imported share (%)")
    bottom_ax.grid(axis="y", alpha=0.25)

    for crossing in summary["crossings"]:
        y_value = crossing.value * 100
        label = (
            f"{crossing.position}\nAbove threshold"
            if crossing.crossed_above
            else f"{crossing.position}\nBelow threshold"
        )
        offset = 1.1 if crossing.crossed_above else 1.8
        bottom_ax.scatter([crossing.position], [y_value], color="#aa2e25", s=40, zorder=3)
        bottom_ax.annotate(
            label,
            xy=(crossing.position, y_value),
            xytext=(crossing.position + 0.3, y_value + offset),
            fontsize=8,
            va="bottom",
            arrowprops={"arrowstyle": "-", "color": "#555555", "lw": 0.8},
        )

    bottom_ax.text(
        years[0] + 0.2,
        threshold_percent + 0.45,
        f"Threshold: {threshold_percent:.0f}%",
        color="#aa2e25",
        fontsize=9,
    )

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_summary(report, path):
    path.write_text(report + "\n", encoding="utf-8")


def repo_relative_path(path):
    return path.relative_to(REPO_ROOT).as_posix()


def main():
    series = load_series(DATA_PATH)
    summary = summarize(series)
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