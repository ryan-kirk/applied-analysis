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
WATCH_THRESHOLD = 0.135
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


def chart_event_label(label):
    aliases = {
        "Global food price spike": "Food price spike",
        "Horn of Africa drought": "Horn drought",
        "Commodity price downturn": "Commodity downturn",
        "Foreign exchange pressure": "FX pressure",
        "Mechanization and digital agriculture growth": "Mechanization growth",
        "Higher-for-longer rates and Red Sea trade disruption": "Rates + Red Sea shock",
    }
    return aliases.get(label, label)


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
    recent_start_index = max(0, len(series) - 3)
    recent_events = [event for event in events if event.year >= years[-1] - 1]

    chart_events = [
        {
            "year": match.event.year,
            "label": match.event.event_name,
            "chart_label": chart_event_label(match.event.event_name),
            "kind": match.timing,
        }
        for match in matches
    ]
    chart_event_years = {(item["year"], item["label"]) for item in chart_events}
    for event in recent_events:
        chart_key = (event.year, event.event_name)
        if chart_key not in chart_event_years:
            chart_events.append(
                {
                    "year": event.year,
                    "label": event.event_name,
                    "chart_label": chart_event_label(event.event_name),
                    "kind": "recent-watch",
                }
            )
    chart_events.sort(key=lambda item: (item["year"], item["label"]))

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
        "watch_threshold": WATCH_THRESHOLD,
        "crossings": crossings,
        "windows": windows,
        "window_summaries": window_summaries,
        "event_matches": matches,
        "chart_events": chart_events,
        "recent_events": recent_events,
        "peak_imported_share": imported_share[peak_index],
        "peak_imported_share_year": years[peak_index],
        "peak_capital_cost": capital_costs[capital_peak_index],
        "peak_capital_cost_year": years[capital_peak_index],
        "latest_imported_share": imported_share[-1],
        "latest_capital_cost": capital_costs[-1],
        "recent_start_year": years[recent_start_index],
        "recent_imported_share_start": imported_share[recent_start_index],
        "recent_capital_cost_start": capital_costs[recent_start_index],
        "recent_imported_share_change_points": imported_share[-1] - imported_share[recent_start_index],
        "recent_capital_cost_change_points": capital_costs[-1] - capital_costs[recent_start_index],
        "recent_watch_triggered": WATCH_THRESHOLD <= imported_share[-1] < THRESHOLD,
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
    first_shift = first_window["average_capital_cost"] - first_window["pre_window_capital_cost"]
    event_count = len(summary["event_matches"])
    recent_event_text = (
        f"One recent backdrop in the curated file is the {summary['recent_events'][-1].year} "
        f"{summary['recent_events'][-1].event_name}."
        if summary["recent_events"]
        else "No recent curated event was added for the latest uptick."
    )
    watch_sentence = (
        f"There is still no third 15% pressure window, but a lower {summary['watch_threshold']:.1%} watch threshold would now flag {summary['end_year']} as a renewed watch year. "
        if summary["recent_watch_triggered"]
        else "The recent move remains below both the main threshold and the candidate watch threshold. "
    )

    return (
        f"The imported-food-share proxy crossed into two sustained pressure windows: "
        f"{summary['windows'][0].start}-{summary['windows'][0].end} and "
        f"{summary['windows'][1].start}-{summary['windows'][1].end}. "
        f"A total of {event_count} curated events fall either in the year before or during those windows, which helps explain what was happening around the pressure episodes without claiming those events caused the threshold crossing. "
        f"Capital costs were already elevated entering the first window and averaged {format_rate(first_window['average_capital_cost'])} during it, "
        f"{first_shift:+.1f} percentage points versus the one-year lead period. "
        f"By the second window, imported-food pressure stayed above threshold even as the capital-cost proxy eased from its {summary['peak_capital_cost_year']} peak, which suggests the signal reflects a wider system context rather than a single financing variable. "
        f"The latest reading is below threshold, but imported-food share has risen from {summary['recent_imported_share_start']:.1%} in {summary['recent_start_year']} to {summary['latest_imported_share']:.1%} in {summary['end_year']}, while the capital-cost proxy rose from {format_rate(summary['recent_capital_cost_start'])} to {format_rate(summary['latest_capital_cost'])}. "
        f"{watch_sentence}{recent_event_text}"
    )


def build_report(summary, interpretation, chart_path=None, summary_path=None):
    lines = [
        "Applied Analysis - Event Context Windows",
        "----------------------------------------",
        f"Question: {QUESTION}",
        f"Region: {REGION_NAME}",
        f"Time range: {summary['start_year']} to {summary['end_year']}",
        f"Threshold signal: Imported food share of available supply proxy above {summary['threshold']:.0%}",
        f"Candidate watch threshold: {summary['watch_threshold']:.1%}",
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

    lines.extend(["", "Recent watch period:"])
    lines.append(
        (
            f"- Imported-food share rose from {summary['recent_imported_share_start']:.1%} in {summary['recent_start_year']} to "
            f"{summary['latest_imported_share']:.1%} in {summary['end_year']} "
            f"({summary['recent_imported_share_change_points'] * 100:+.1f} percentage points)."
        )
    )
    lines.append(
        (
            f"- Capital-cost proxy rose from {format_rate(summary['recent_capital_cost_start'])} in {summary['recent_start_year']} to "
            f"{format_rate(summary['latest_capital_cost'])} in {summary['end_year']} "
            f"({summary['recent_capital_cost_change_points']:+.1f} percentage points)."
        )
    )
    if summary["recent_watch_triggered"]:
        lines.append(
            f"- A lower {summary['watch_threshold']:.1%} watch threshold would flag {summary['end_year']} as a renewed watch year, even though the main 15% threshold has not been crossed again."
        )
    if summary["recent_events"]:
        recent_event_text = "; ".join(
            f"{event.year} {event.event_name}" for event in summary["recent_events"]
        )
        lines.append(f"- Recent context event(s): {recent_event_text}.")

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
    population = [point["population"] / 1_000_000 for point in series]
    imported_share = [point["imported_food_share_of_supply"] * 100 for point in series]
    capital_costs = [point["ssa_capital_cost_proxy"] for point in series]
    threshold_percent = summary["threshold"] * 100
    watch_threshold_percent = summary["watch_threshold"] * 100

    fig, (top_ax, bottom_ax) = plt.subplots(
        2,
        1,
        figsize=(11, 8.6),
        sharex=True,
        height_ratios=[0.72, 1.48],
    )
    top_ax_right = top_ax.twinx()
    bottom_ax_right = bottom_ax.twinx()

    top_ax.plot(years, agriculture, marker="o", linewidth=2.3, color="#2f6b3b", label="Agriculture value added")
    top_ax.plot(years, imports, marker="o", linewidth=2.3, color="#c46b2c", label="Estimated food imports")
    top_ax_right.plot(
        years,
        population,
        linewidth=2.2,
        linestyle=":",
        color="#6b4ea0",
        label="Population",
    )
    top_ax.set_title("SSA Agricultural Capital Pressure")
    top_ax.set_ylabel("USD (billions)")
    top_ax_right.set_ylabel("Population (millions)")
    top_ax.grid(axis="y", alpha=0.25)
    top_handles, top_labels = top_ax.get_legend_handles_labels()
    top_right_handles, top_right_labels = top_ax_right.get_legend_handles_labels()
    top_ax.legend(top_handles + top_right_handles, top_labels + top_right_labels, frameon=False, loc="upper left")

    for window in summary["windows"]:
        bottom_ax.axvspan(window.start, window.end, color="#f3d8c0", alpha=0.45)

    bottom_ax.plot(years, imported_share, marker="o", linewidth=2.4, color="#204a87", label="Imported share")
    bottom_ax_right.plot(
        years,
        capital_costs,
        marker="o",
        linewidth=2.2,
        linestyle="--",
        color="#8f4f8b",
        label="Capital cost proxy",
    )
    bottom_ax.axhline(threshold_percent, color="#aa2e25", linestyle="--", linewidth=1.8)
    bottom_ax.axhline(watch_threshold_percent, color="#d48734", linestyle=":", linewidth=1.6)
    bottom_ax.set_ylabel("Imported share (%)")
    bottom_ax_right.set_ylabel("Capital cost proxy (%)")
    bottom_ax.grid(axis="y", alpha=0.25)

    share_min = min(imported_share)
    share_max = max(max(imported_share), threshold_percent, watch_threshold_percent)
    bottom_ax.set_ylim(share_min - 0.8, share_max + 5.8)
    bottom_ax_right.set_ylim(min(capital_costs) - 0.8, max(capital_costs) + 1.0)
    bottom_ax.set_xlim(years[0] - 1.2, years[-1] + 1.2)

    def segments_intersect(segment_a, segment_b):
        def orientation(point_a, point_b, point_c):
            value = ((point_b[1] - point_a[1]) * (point_c[0] - point_b[0])) - ((point_b[0] - point_a[0]) * (point_c[1] - point_b[1]))
            if abs(value) < 1e-9:
                return 0
            return 1 if value > 0 else 2

        def on_segment(point_a, point_b, point_c):
            return (
                min(point_a[0], point_c[0]) <= point_b[0] <= max(point_a[0], point_c[0])
                and min(point_a[1], point_c[1]) <= point_b[1] <= max(point_a[1], point_c[1])
            )

        point_a, point_b = segment_a
        point_c, point_d = segment_b
        orientation_1 = orientation(point_a, point_b, point_c)
        orientation_2 = orientation(point_a, point_b, point_d)
        orientation_3 = orientation(point_c, point_d, point_a)
        orientation_4 = orientation(point_c, point_d, point_b)

        if orientation_1 != orientation_2 and orientation_3 != orientation_4:
            return True
        if orientation_1 == 0 and on_segment(point_a, point_c, point_b):
            return True
        if orientation_2 == 0 and on_segment(point_a, point_d, point_b):
            return True
        if orientation_3 == 0 and on_segment(point_c, point_a, point_d):
            return True
        if orientation_4 == 0 and on_segment(point_c, point_b, point_d):
            return True
        return False

    def boxes_overlap(box_a, box_b):
        return not (
            box_a[1] < box_b[0]
            or box_b[1] < box_a[0]
            or box_a[3] < box_b[2]
            or box_b[3] < box_a[2]
        )

    def wrap_label_text(year, label, max_line_length=22):
        if len(label) <= max_line_length:
            return f"{year} {label}"

        midpoint = len(label) // 2
        split_points = [index for index, char in enumerate(label) if char == " "]
        if not split_points:
            return f"{year}\n{label}"

        split_index = min(split_points, key=lambda index: abs(index - midpoint))
        first_line = label[:split_index].strip()
        second_line = label[split_index + 1 :].strip()
        if len(second_line) > max_line_length + 6:
            second_line = second_line[: max_line_length + 3].rstrip() + "..."
        return f"{year} {first_line}\n{second_line}"

    ymin, ymax = bottom_ax.get_ylim()
    xmin, xmax = bottom_ax.get_xlim()
    upper_y_levels = [ymax - 0.6, ymax - 1.55, ymax - 2.5, ymax - 3.45, ymax - 4.4, ymax - 5.15]
    lower_y_levels = [ymin + 0.6, ymin + 1.7, ymin + 2.8, ymin + 3.9, ymin + 5.0]
    x_offset_candidates = [0.35, -0.55, 1.0, -1.2, 1.8, -2.0, 2.7, -2.9, 3.6, -3.8]
    placed_segments = []
    placed_label_boxes = []

    for index, chart_event in enumerate(summary["chart_events"]):
        event_year = chart_event["year"]
        label_text = wrap_label_text(event_year, chart_event["chart_label"])
        event_value = next(
            point["imported_food_share_of_supply"] * 100 for point in series if point["year"] == event_year
        )
        place_below = event_value < threshold_percent
        candidate_y_levels = lower_y_levels if place_below else upper_y_levels
        vertical_alignment = "top" if place_below else "bottom"
        marker_color = "#aa2e25" if chart_event["kind"] != "recent-watch" else "#d48734"
        best_candidate = None
        longest_line_length = max(len(line) for line in label_text.splitlines())
        label_width = max(2.0, min(5.2, longest_line_length * 0.08))
        label_height = 0.42 * len(label_text.splitlines()) + 0.18

        for candidate_y in candidate_y_levels:
            for x_offset in x_offset_candidates:
                text_x = event_year + x_offset
                if not (xmin + 0.4 <= text_x <= xmax - 0.4):
                    continue

                jitter_pattern = [-0.7, -0.35, 0.0, 0.35, 0.7]
                jitter = jitter_pattern[index % len(jitter_pattern)]
                if place_below:
                    candidate_text_y = candidate_y - jitter
                else:
                    candidate_text_y = candidate_y + jitter

                if chart_event["kind"] == "recent-watch" and event_year >= years[-1]:
                    candidate_text_y -= 1.8

                leader_segment = ((event_year, event_value), (text_x, candidate_text_y))
                crossing_penalty = sum(
                    100 for existing_segment in placed_segments if segments_intersect(leader_segment, existing_segment)
                )
                horizontal_alignment = "left" if text_x >= event_year else "right"
                if horizontal_alignment == "left":
                    label_box = (text_x - 0.1, text_x + label_width, candidate_text_y - label_height, candidate_text_y + label_height)
                else:
                    label_box = (text_x - label_width, text_x + 0.1, candidate_text_y - label_height, candidate_text_y + label_height)

                overlap_penalty = sum(90 for existing_box in placed_label_boxes if boxes_overlap(label_box, existing_box))

                vertical_spacing_penalty = 0
                for existing_box in placed_label_boxes:
                    vertical_gap = min(abs(label_box[2] - existing_box[3]), abs(existing_box[2] - label_box[3]))
                    horizontal_overlap = not (label_box[1] < existing_box[0] or existing_box[1] < label_box[0])
                    if horizontal_overlap and vertical_gap < 0.55:
                        vertical_spacing_penalty += 28

                distance_score = ((text_x - event_year) ** 2 + ((candidate_text_y - event_value) / 1.6) ** 2) ** 0.5
                side_penalty = 0
                if event_year <= years[2] and x_offset < 0:
                    side_penalty += 5
                if event_year >= years[-3] and x_offset > 0:
                    side_penalty += 8
                if text_x < event_year - 2.6 or text_x > event_year + 2.6:
                    side_penalty += 1.5
                if chart_event["kind"] == "recent-watch" and event_year >= years[-1] and candidate_text_y > event_value - 0.9:
                    side_penalty += 28

                score = distance_score + crossing_penalty + overlap_penalty + vertical_spacing_penalty + side_penalty
                if best_candidate is None or score < best_candidate["score"]:
                    best_candidate = {
                        "text_x": text_x,
                        "text_y": candidate_text_y,
                        "label_box": label_box,
                        "score": score,
                    }

        if best_candidate is None:
            fallback_y = candidate_y_levels[0]
            fallback_x = max(min(event_year + 0.35, xmax - 0.5), xmin + 0.5)
            best_candidate = {"text_x": fallback_x, "text_y": fallback_y, "score": 0}

        text_x = best_candidate["text_x"]
        text_y = best_candidate["text_y"]
        horizontal_alignment = "left" if text_x >= event_year else "right"
        placed_segments.append(((event_year, event_value), (text_x, text_y)))
        placed_label_boxes.append(best_candidate["label_box"])

        bottom_ax.axvline(event_year, color="#666666", alpha=0.18, linewidth=1)
        bottom_ax.scatter([event_year], [event_value], color=marker_color, s=35, zorder=3)
        bottom_ax.annotate(
            label_text,
            xy=(event_year, event_value),
            xytext=(text_x, text_y),
            xycoords="data",
            textcoords="data",
            fontsize=7.5,
            ha=horizontal_alignment,
            va=vertical_alignment,
            bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "none", "alpha": 0.9},
            arrowprops={"arrowstyle": "-", "color": "#555555", "lw": 0.8},
        )

    bottom_ax.text(
        years[0] + 0.2,
        threshold_percent + 0.35,
        f"Threshold: {threshold_percent:.0f}%",
        color="#aa2e25",
        fontsize=9,
    )
    bottom_ax.set_xlabel("Year")
    bottom_ax.text(
        years[0] + 0.2,
        watch_threshold_percent + 0.2,
        f"Watch threshold: {watch_threshold_percent:.1f}%",
        color="#d48734",
        fontsize=8.5,
    )

    bottom_handles, bottom_labels = bottom_ax.get_legend_handles_labels()
    bottom_right_handles, bottom_right_labels = bottom_ax_right.get_legend_handles_labels()
    bottom_ax.legend(
        bottom_handles + bottom_right_handles,
        bottom_labels + bottom_right_labels,
        frameon=False,
        loc="upper left",
    )

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