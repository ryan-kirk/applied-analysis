from csv import DictReader
from datetime import date
import os
from pathlib import Path
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
DATA_PATH = BASE_DIR / "data" / "us_10_year_treasury_rate.csv"
CHART_PATH = BASE_DIR / "trend_signal.png"
SUMMARY_PATH = BASE_DIR / "trend_signal_summary.txt"
SIGNAL_NAME = "Interest Rates (10-Year Treasury Rate)"


def load_series(path):
    with path.open(newline="") as file:
        return [
            {"date": date.fromisoformat(row["date"]), "value": float(row["value"])}
            for row in DictReader(file)
        ]


def direction_for(change):
    if abs(change) < 0.25:
        return "stable"
    return "increasing" if change > 0 else "decreasing"


def strength_for(change):
    amount = abs(change)

    if amount < 0.5:
        return "minor"
    if amount < 1.5:
        return "moderate"
    return "meaningful"


def pattern_for(series, change):
    if direction_for(change) == "stable":
        return "mostly stable"

    step_changes = [
        series[index]["value"] - series[index - 1]["value"]
        for index in range(1, len(series))
    ]
    total_movement = sum(abs(step) for step in step_changes)

    if total_movement == 0:
        return "mostly stable"

    directness = abs(change) / total_movement
    return "steady" if directness >= 0.70 else "uneven, but clearly directional"


def display_label(value):
    return value[:1].upper() + value[1:]


def summarize_change(series):
    start = series[0]
    end = series[-1]
    change = end["value"] - start["value"]
    percent_change = (change / start["value"]) * 100 if start["value"] else 0
    years = (end["date"] - start["date"]).days / 365.25
    average_yearly_change = change / years if years else 0

    return {
        "signal_name": SIGNAL_NAME,
        "start_date": start["date"],
        "end_date": end["date"],
        "start_value": start["value"],
        "end_value": end["value"],
        "change": change,
        "percent_change": percent_change,
        "average_yearly_change": average_yearly_change,
        "direction": direction_for(change),
        "strength": strength_for(change),
        "pattern": pattern_for(series, change),
    }


def interpret(summary):
    if summary["direction"] == "stable":
        return (
            "The 10-year Treasury rate stayed close to where it started. "
            "The main thing to notice is that there was no strong movement "
            "in long-term interest rates over this period."
        )

    direction_text = "higher" if summary["direction"] == "increasing" else "lower"
    pattern_text = (
        "The path was fairly steady."
        if summary["pattern"] == "steady"
        else "The path moved around along the way, but the overall shift is clear."
    )

    return (
        f"The 10-year Treasury rate ended {direction_text} than where it began, "
        f"moving from {summary['start_value']:.2f}% to {summary['end_value']:.2f}%. "
        f"{pattern_text} This matters because long-term rates shape borrowing costs "
        "for households, companies, and public budgets."
    )


def build_report(summary, interpretation, chart_path=None, summary_path=None):
    lines = [
        "Applied Analysis - Trend Signal",
        "----------------------------------------",
        f"Signal: {summary['signal_name']}",
        f"Time range: {summary['start_date']} to {summary['end_date']}",
        (
            "Absolute change: "
            f"{summary['change']:+.2f} percentage points "
            f"({summary['start_value']:.2f}% to {summary['end_value']:.2f}%)"
        ),
        f"Percent change: {summary['percent_change']:+.1f}%",
        (
            "Average yearly movement: "
            f"{summary['average_yearly_change']:+.2f} percentage points per year"
        ),
        f"Direction: {display_label(summary['direction'])}",
        f"Strength: {display_label(summary['strength'])}",
        f"Pattern: {display_label(summary['pattern'])}",
        "",
        "What to notice:",
        interpretation,
    ]

    if chart_path or summary_path:
        lines.extend(["", "Artifacts:"])

    if chart_path:
        lines.append(f"Chart: {chart_path}")

    if summary_path:
        lines.append(f"Summary: {summary_path}")

    return "\n".join(lines)


def save_chart(series, path):
    dates = [point["date"] for point in series]
    values = [point["value"] for point in series]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(dates, values, marker="o", linewidth=2)
    ax.set_title("Trend Signal: 10-Year Treasury Rate")
    ax.set_xlabel("Date")
    ax.set_ylabel("Rate (%)")
    ax.grid(axis="y", alpha=0.25)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_summary(report, path):
    path.write_text(report + "\n", encoding="utf-8")


def repo_relative_path(path):
    return path.relative_to(REPO_ROOT).as_posix()


def main():
    series = load_series(DATA_PATH)
    summary = summarize_change(series)
    interpretation = interpret(summary)

    save_chart(series, CHART_PATH)
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
