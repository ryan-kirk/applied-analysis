from csv import DictReader
import math
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
DATA_PATH = BASE_DIR / "data" / "kidney_transplant_system_signals.csv"
CHART_PATH = BASE_DIR / "kidney_transplant_signal_comparison.png"
SUMMARY_PATH = BASE_DIR / "kidney_transplant_signal_comparison_summary.txt"
SIGNAL_A_NAME = "Kidney transplants performed"
SIGNAL_B_NAME = "Kidney waitlist additions"


def load_series(path):
    with path.open(newline="", encoding="utf-8") as file:
        return [
            {
                "year": int(row["year"]),
                "kidney_transplants": int(row["kidney_transplants"]),
                "kidney_waitlist_additions": int(row["kidney_waitlist_additions"]),
            }
            for row in DictReader(file)
        ]


def percent_change(start, end):
    if start == 0:
        return 0.0
    return ((end - start) / start) * 100


def correlation(values_a, values_b):
    if len(values_a) != len(values_b) or len(values_a) < 2:
        return 0.0

    mean_a = sum(values_a) / len(values_a)
    mean_b = sum(values_b) / len(values_b)
    numerator = 0.0
    variance_a = 0.0
    variance_b = 0.0

    for value_a, value_b in zip(values_a, values_b):
        centered_a = value_a - mean_a
        centered_b = value_b - mean_b
        numerator += centered_a * centered_b
        variance_a += centered_a * centered_a
        variance_b += centered_b * centered_b

    if variance_a == 0 or variance_b == 0:
        return 0.0

    return numerator / math.sqrt(variance_a * variance_b)


def year_over_year_changes(values):
    return [
        percent_change(previous, current)
        for previous, current in zip(values[:-1], values[1:])
    ]


def direction_for(change_percent):
    if abs(change_percent) < 5:
        return "stable"
    return "increasing" if change_percent > 0 else "decreasing"


def relationship_for(direction_a, direction_b, level_correlation):
    if direction_a == direction_b and direction_a != "stable" and level_correlation >= 0.7:
        return "moving together"
    if direction_a != direction_b and "stable" not in {direction_a, direction_b}:
        return "moving apart"
    return "mixed"


def lag_signal_for(level_correlation, lag_correlation):
    if lag_correlation >= level_correlation + 0.08:
        return "possible one-year lag"
    return "no clear lag"


def summarize(series):
    years = [point["year"] for point in series]
    transplants = [point["kidney_transplants"] for point in series]
    waitlist_additions = [point["kidney_waitlist_additions"] for point in series]

    transplant_change_percent = percent_change(transplants[0], transplants[-1])
    waitlist_change_percent = percent_change(waitlist_additions[0], waitlist_additions[-1])
    level_correlation = correlation(transplants, waitlist_additions)
    year_change_correlation = correlation(
        year_over_year_changes(transplants),
        year_over_year_changes(waitlist_additions),
    )
    lag_correlation = correlation(transplants[1:], waitlist_additions[:-1])
    start_gap = waitlist_additions[0] - transplants[0]
    end_gap = waitlist_additions[-1] - transplants[-1]
    start_ratio = transplants[0] / waitlist_additions[0]
    end_ratio = transplants[-1] / waitlist_additions[-1]
    direction_a = direction_for(transplant_change_percent)
    direction_b = direction_for(waitlist_change_percent)

    return {
        "start_year": years[0],
        "end_year": years[-1],
        "signal_a_name": SIGNAL_A_NAME,
        "signal_b_name": SIGNAL_B_NAME,
        "signal_a_start": transplants[0],
        "signal_a_end": transplants[-1],
        "signal_b_start": waitlist_additions[0],
        "signal_b_end": waitlist_additions[-1],
        "signal_a_change_percent": transplant_change_percent,
        "signal_b_change_percent": waitlist_change_percent,
        "signal_a_direction": direction_a,
        "signal_b_direction": direction_b,
        "relationship": relationship_for(direction_a, direction_b, level_correlation),
        "lag_signal": lag_signal_for(level_correlation, lag_correlation),
        "level_correlation": level_correlation,
        "year_change_correlation": year_change_correlation,
        "lag_correlation": lag_correlation,
        "start_gap": start_gap,
        "end_gap": end_gap,
        "start_ratio": start_ratio,
        "end_ratio": end_ratio,
    }


def interpret(summary):
    relationship = summary["relationship"]
    lag_signal = summary["lag_signal"]
    ratio_change = summary["end_ratio"] - summary["start_ratio"]

    if relationship == "moving together":
        relationship_text = (
            "The two system signals mostly moved together over this period. "
        )
    elif relationship == "moving apart":
        relationship_text = (
            "The two system signals moved in different directions over this period. "
        )
    else:
        relationship_text = (
            "The two system signals showed a mixed relationship over this period. "
        )

    if ratio_change > 0:
        ratio_text = (
            "Transplant volume improved slightly relative to incoming waitlist demand, "
            "but demand still stayed much larger than the number of transplants performed."
        )
    else:
        ratio_text = (
            "Transplant volume did not keep pace with incoming waitlist demand."
        )

    return (
        f"{relationship_text}Kidney transplants rose from "
        f"{summary['signal_a_start']:,} to {summary['signal_a_end']:,}, while annual kidney "
        f"waitlist additions rose from {summary['signal_b_start']:,} to "
        f"{summary['signal_b_end']:,}. {ratio_text} In this annual view, there is "
        f"{lag_signal}, so the clearest signal is persistent system pressure rather than a "
        "simple delayed response."
    )


def build_report(summary, interpretation, chart_path=None, summary_path=None):
    lines = [
        "Applied Analysis - Signal Comparison",
        "----------------------------------------",
        "Question: How does kidney transplant volume relate to kidney waitlist demand over time?",
        f"Time range: {summary['start_year']} to {summary['end_year']}",
        f"Signal A: {summary['signal_a_name']}",
        (
            f"  {summary['signal_a_start']:,} -> {summary['signal_a_end']:,} "
            f"({summary['signal_a_change_percent']:+.1f}%)"
        ),
        f"Signal B: {summary['signal_b_name']}",
        (
            f"  {summary['signal_b_start']:,} -> {summary['signal_b_end']:,} "
            f"({summary['signal_b_change_percent']:+.1f}%)"
        ),
        f"Relationship: {summary['relationship'].title()}",
        f"Possible lag: {summary['lag_signal'].title()}",
        f"Level correlation: {summary['level_correlation']:.2f}",
        f"Year-over-year change correlation: {summary['year_change_correlation']:.2f}",
        f"Demand minus transplants gap: {summary['start_gap']:,} -> {summary['end_gap']:,}",
        (
            "Transplants as a share of waitlist additions: "
            f"{summary['start_ratio']:.1%} -> {summary['end_ratio']:.1%}"
        ),
        "",
        "What to notice:",
        interpretation,
        "",
        "Source note:",
        (
            "This example uses annual kidney transplants and annual kidney waitlist additions "
            "from the public OPTN Metrics dashboard. Waitlist additions are used here as a "
            "transparent proxy for waitlist demand in a small, local example."
        ),
    ]

    if chart_path or summary_path:
        lines.extend(["", "Artifacts:"])

    if chart_path:
        lines.append(f"Chart: {chart_path}")

    if summary_path:
        lines.append(f"Summary: {summary_path}")

    return "\n".join(lines)


def save_chart(series, path):
    years = [point["year"] for point in series]
    transplants = [point["kidney_transplants"] for point in series]
    waitlist_additions = [point["kidney_waitlist_additions"] for point in series]

    fig, ax = plt.subplots(figsize=(8.5, 4.75))
    ax.plot(years, transplants, marker="o", linewidth=2.4, label=SIGNAL_A_NAME)
    ax.plot(
        years,
        waitlist_additions,
        marker="o",
        linewidth=2.4,
        label=SIGNAL_B_NAME,
    )
    ax.set_title("Kidney Transplant System Signals")
    ax.set_xlabel("Year")
    ax.set_ylabel("People")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_summary(report, path):
    path.write_text(report + "\n", encoding="utf-8")


def main():
    series = load_series(DATA_PATH)
    summary = summarize(series)
    interpretation = interpret(summary)

    save_chart(series, CHART_PATH)
    summary_report = build_report(summary, interpretation)
    save_summary(summary_report, SUMMARY_PATH)

    console_report = build_report(
        summary,
        interpretation,
        chart_path=CHART_PATH.resolve(),
        summary_path=SUMMARY_PATH.resolve(),
    )
    print(console_report)


if __name__ == "__main__":
    main()