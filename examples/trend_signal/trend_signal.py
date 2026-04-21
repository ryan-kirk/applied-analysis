from csv import DictReader
from pathlib import Path


DATA_PATH = Path(__file__).parent / "data" / "sample_timeseries.csv"


def load_series(path):
    with path.open(newline="") as file:
        return [
            {"date": row["date"], "value": float(row["value"])}
            for row in DictReader(file)
        ]


def classify_signal(percent_change):
    if abs(percent_change) < 2:
        return "stable"
    if abs(percent_change) < 10:
        return "moderate upward movement" if percent_change > 0 else "moderate downward movement"
    return "meaningful upward movement" if percent_change > 0 else "meaningful downward movement"


def summarize_change(series):
    start = series[0]
    end = series[-1]
    change = end["value"] - start["value"]
    percent_change = (change / start["value"]) * 100 if start["value"] else 0

    return {
        "start_date": start["date"],
        "end_date": end["date"],
        "start_value": start["value"],
        "end_value": end["value"],
        "change": change,
        "percent_change": percent_change,
        "signal": classify_signal(percent_change),
    }


def interpret(summary):
    signal = summary["signal"]

    if signal == "stable":
        return "The values stayed close to where they started, so there is no strong movement to act on."

    if "upward" in signal:
        return "The values moved up enough to stand out. A decision-maker should notice the upward shift and keep watching whether it continues."

    return "The values moved down enough to stand out. A decision-maker should notice the downward shift and consider what may be driving it."


def main():
    series = load_series(DATA_PATH)
    summary = summarize_change(series)

    print("Applied Analysis: Trend Signal")
    print("=" * 38)
    print(f"Data: {summary['start_date']} to {summary['end_date']}")
    print(
        "Change: "
        f"{summary['start_value']:.0f} to {summary['end_value']:.0f} "
        f"({summary['change']:+.0f}, {summary['percent_change']:+.1f}%)"
    )
    print(f"Signal: {summary['signal']}")
    print(f"Interpretation: {interpret(summary)}")


if __name__ == "__main__":
    main()
