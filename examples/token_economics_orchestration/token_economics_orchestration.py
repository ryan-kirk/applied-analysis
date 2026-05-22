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
from applied_analysis.signal_comparison import classify_trend_direction, compare_signal_directions
from applied_analysis.thresholds import detect_threshold_runs, format_duration


TITLE = "When Cheap Tokens Get Expensive: The Hidden Cost of Agentic Workflows"
QUESTION = "Are falling token prices reducing cost per task, or are agents and orchestration increasing token usage enough to offset the savings?"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
PRICING_PATH = DATA_DIR / "vendor_model_pricing.csv"
TASKS_PATH = DATA_DIR / "task_token_profiles.csv"
PATTERNS_PATH = DATA_DIR / "orchestration_patterns.csv"
EVENTS_PATH = DATA_DIR / "token_market_events.csv"
SCENARIOS_PATH = OUTPUT_DIR / "token_cost_scenarios.csv"
SUMMARY_PATH = OUTPUT_DIR / "token_economics_summary.csv"
CHART_PATH = OUTPUT_DIR / "token_economics_orchestration.png"

ANALYSIS_YEARS = [2023, 2024, 2025, 2026]
MODEL_FAMILY_BY_TASK = {
    "support": "budget",
    "research": "balanced",
    "coding": "balanced",
    "orchestration": "flagship",
}
TASK_MIX_BY_YEAR = {
    2023: {"support": 0.40, "research": 0.30, "coding": 0.20, "orchestration": 0.10},
    2024: {"support": 0.32, "research": 0.28, "coding": 0.25, "orchestration": 0.15},
    2025: {"support": 0.24, "research": 0.24, "coding": 0.30, "orchestration": 0.22},
    2026: {"support": 0.18, "research": 0.20, "coding": 0.32, "orchestration": 0.30},
}
PATTERN_MIX_BY_YEAR = {
    2023: {"direct_prompt": 0.55, "rag_assisted": 0.30, "plan_execute": 0.10, "planner_critic": 0.05},
    2024: {"direct_prompt": 0.35, "rag_assisted": 0.30, "plan_execute": 0.22, "planner_critic": 0.13},
    2025: {"direct_prompt": 0.22, "rag_assisted": 0.28, "plan_execute": 0.30, "planner_critic": 0.20},
    2026: {"direct_prompt": 0.14, "rag_assisted": 0.20, "plan_execute": 0.35, "planner_critic": 0.31},
}
REALIZED_CACHE_FACTOR_BY_YEAR = {
    2023: 0.20,
    2024: 0.45,
    2025: 0.72,
    2026: 0.95,
}

ORCHESTRATION_INFLATION_THRESHOLD = 3.0
CACHED_DISCOUNT_THRESHOLD = 0.80
COST_DECLINE_THRESHOLD = 0.50


def load_vendor_pricing(path):
    with path.open(newline="", encoding="utf-8") as file:
        return [
            {
                "effective_date": datetime.strptime(row["effective_date"], "%Y-%m-%d").date(),
                "vendor": row["vendor"].strip(),
                "model": row["model"].strip(),
                "model_family": row["model_family"].strip(),
                "input_per_1m_usd": float(row["input_per_1m_usd"]),
                "output_per_1m_usd": float(row["output_per_1m_usd"]),
                "cached_input_per_1m_usd": float(row["cached_input_per_1m_usd"]),
                "context_window_tokens": int(row["context_window_tokens"]),
                "pricing_url": row["pricing_url"].strip(),
                "notes": row["notes"].strip(),
            }
            for row in DictReader(file)
        ]


def load_task_profiles(path):
    with path.open(newline="", encoding="utf-8") as file:
        return [
            {
                "task_type": row["task_type"].strip(),
                "task_name": row["task_name"].strip(),
                "description": row["description"].strip(),
                "input_tokens": int(row["input_tokens"]),
                "output_tokens": int(row["output_tokens"]),
                "cacheable_input_tokens": int(row["cacheable_input_tokens"]),
                "retrieval_tokens": int(row["retrieval_tokens"]),
                "tool_result_tokens": int(row["tool_result_tokens"]),
                "human_review_tokens": int(row["human_review_tokens"]),
                "expected_runs_per_task": int(row["expected_runs_per_task"]),
                "notes": row["notes"].strip(),
            }
            for row in DictReader(file)
        ]


def load_patterns(path):
    with path.open(newline="", encoding="utf-8") as file:
        return [
            {
                "pattern_id": row["pattern_id"].strip(),
                "pattern_name": row["pattern_name"].strip(),
                "description": row["description"].strip(),
                "planner_calls": int(row["planner_calls"]),
                "retriever_calls": int(row["retriever_calls"]),
                "tool_calls": int(row["tool_calls"]),
                "critic_calls": int(row["critic_calls"]),
                "executor_calls": int(row["executor_calls"]),
                "average_context_tokens_per_call": int(row["average_context_tokens_per_call"]),
                "average_output_tokens_per_call": int(row["average_output_tokens_per_call"]),
                "loop_count": int(row["loop_count"]),
                "cache_reuse_rate": float(row["cache_reuse_rate"]),
                "notes": row["notes"].strip(),
            }
            for row in DictReader(file)
        ]


def load_market_events(path):
    with path.open(newline="", encoding="utf-8") as file:
        events = []
        for row in DictReader(file):
            event_date = datetime.strptime(row["event_date"], "%Y-%m-%d").date()
            events.append(
                {
                    "event_date": event_date,
                    "event_year": event_date.year,
                    "event_type": row["event_type"].strip(),
                    "event_name": row["event_name"].strip(),
                    "vendor": row["vendor"].strip(),
                    "description": row["description"].strip(),
                    "source_url": row["source_url"].strip(),
                    "relevance": row["relevance"].strip(),
                }
            )
        return events


def choose_market_model(pricing_rows, family, year):
    candidates = [
        row
        for row in pricing_rows
        if row["model_family"] == family and row["effective_date"].year <= year
    ]
    if not candidates:
        raise ValueError(f"No pricing row found for {family} in or before {year}")

    return min(
        candidates,
        key=lambda row: (
            row["input_per_1m_usd"] + row["output_per_1m_usd"],
            -row["effective_date"].toordinal(),
        ),
    )


def average(values):
    if not values:
        return 0.0
    return sum(values) / len(values)


def weighted_average(rows, key):
    total_weight = sum(row["scenario_share"] for row in rows)
    if total_weight == 0:
        return 0.0
    return sum(row[key] * row["scenario_share"] for row in rows) / total_weight


def percent_change(start, end):
    if start == 0:
        return 0.0
    return (end - start) / start


def format_currency(value):
    return f"${value:.2f}"


def format_ratio(value):
    return f"{value:.2f}x"


def format_percent(value):
    return f"{value:.1%}"


def year_fraction(event_date):
    start_of_year = datetime(event_date.year, 1, 1).date()
    end_of_year = datetime(event_date.year + 1, 1, 1).date()
    elapsed = (event_date - start_of_year).days
    duration = (end_of_year - start_of_year).days
    return event_date.year + (elapsed / duration)


def pattern_call_count(pattern):
    return sum(
        [
            pattern["planner_calls"],
            pattern["retriever_calls"],
            pattern["tool_calls"],
            pattern["critic_calls"],
            pattern["executor_calls"],
        ]
    )


def compute_scenario_row(year, task, pattern, model, cache_factor):
    run_count = task["expected_runs_per_task"]
    call_count = max(1, pattern_call_count(pattern))
    looped_calls = call_count * pattern["loop_count"]

    baseline_input_tokens = (
        task["input_tokens"]
        + task["retrieval_tokens"]
        + task["tool_result_tokens"]
        + task["human_review_tokens"]
    ) * run_count
    baseline_output_tokens = task["output_tokens"] * run_count
    baseline_total_tokens = baseline_input_tokens + baseline_output_tokens

    orchestration_input_overhead = (
        pattern["average_context_tokens_per_call"] * looped_calls * run_count
    )
    orchestration_output_overhead = (
        pattern["average_output_tokens_per_call"] * looped_calls * run_count
    )
    repeated_cacheable_input = (
        task["cacheable_input_tokens"] * max(looped_calls - 1, 0) * run_count
    )
    cached_input_tokens = repeated_cacheable_input * pattern["cache_reuse_rate"] * cache_factor

    gross_input_tokens = baseline_input_tokens + orchestration_input_overhead + repeated_cacheable_input
    output_tokens = baseline_output_tokens + orchestration_output_overhead
    total_tokens = gross_input_tokens + output_tokens
    net_input_tokens = gross_input_tokens - cached_input_tokens

    gross_cost_per_task = (
        (gross_input_tokens / 1_000_000) * model["input_per_1m_usd"]
        + (output_tokens / 1_000_000) * model["output_per_1m_usd"]
    )
    net_cost_per_task = (
        (net_input_tokens / 1_000_000) * model["input_per_1m_usd"]
        + (cached_input_tokens / 1_000_000) * model["cached_input_per_1m_usd"]
        + (output_tokens / 1_000_000) * model["output_per_1m_usd"]
    )
    cached_discount_ratio = (
        cached_input_tokens / repeated_cacheable_input if repeated_cacheable_input else 0.0
    )
    orchestration_inflation_factor = (
        total_tokens / baseline_total_tokens if baseline_total_tokens else 1.0
    )

    return {
        "year": year,
        "task_type": task["task_type"],
        "task_name": task["task_name"],
        "pattern_id": pattern["pattern_id"],
        "pattern_name": pattern["pattern_name"],
        "model_family": model["model_family"],
        "vendor": model["vendor"],
        "model": model["model"],
        "scenario_share": TASK_MIX_BY_YEAR[year][task["task_type"]] * PATTERN_MIX_BY_YEAR[year][pattern["pattern_id"]],
        "baseline_total_tokens": baseline_total_tokens,
        "gross_input_tokens": gross_input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "orchestration_inflation_factor": orchestration_inflation_factor,
        "cached_discount_ratio": cached_discount_ratio,
        "gross_cost_per_task": gross_cost_per_task,
        "net_cost_per_task": net_cost_per_task,
        "selected_input_per_1m_usd": model["input_per_1m_usd"],
        "selected_output_per_1m_usd": model["output_per_1m_usd"],
        "selected_cached_input_per_1m_usd": model["cached_input_per_1m_usd"],
        "selected_context_window_tokens": model["context_window_tokens"],
    }


def summarize_year(year, scenario_rows):
    total_tokens = weighted_average(scenario_rows, "total_tokens")
    gross_cost = weighted_average(scenario_rows, "gross_cost_per_task")
    net_cost = weighted_average(scenario_rows, "net_cost_per_task")
    input_tokens = weighted_average(scenario_rows, "gross_input_tokens")
    output_tokens = weighted_average(scenario_rows, "output_tokens")
    blended_token_price = (gross_cost / total_tokens) * 1_000_000 if total_tokens else 0.0
    blended_net_token_price = (net_cost / total_tokens) * 1_000_000 if total_tokens else 0.0
    blended_input_price = (
        sum(row["selected_input_per_1m_usd"] * row["scenario_share"] for row in scenario_rows)
        / sum(row["scenario_share"] for row in scenario_rows)
    )
    blended_output_price = (
        sum(row["selected_output_per_1m_usd"] * row["scenario_share"] for row in scenario_rows)
        / sum(row["scenario_share"] for row in scenario_rows)
    )

    return {
        "year": year,
        "weighted_baseline_tokens_per_task": weighted_average(scenario_rows, "baseline_total_tokens"),
        "weighted_tokens_per_task": total_tokens,
        "weighted_input_tokens_per_task": input_tokens,
        "weighted_output_tokens_per_task": output_tokens,
        "weighted_orchestration_inflation_factor": weighted_average(
            scenario_rows, "orchestration_inflation_factor"
        ),
        "weighted_cached_discount_ratio": weighted_average(
            scenario_rows, "cached_discount_ratio"
        ),
        "weighted_gross_cost_per_task": gross_cost,
        "weighted_net_cost_per_task": net_cost,
        "blended_token_price_per_1m_usd": blended_token_price,
        "blended_net_token_price_per_1m_usd": blended_net_token_price,
        "blended_input_price_per_1m_usd": blended_input_price,
        "blended_output_price_per_1m_usd": blended_output_price,
    }


def attach_cost_decline(year_summaries):
    baseline_cost = year_summaries[0]["weighted_net_cost_per_task"]
    for summary in year_summaries:
        summary["cost_decline_vs_baseline"] = 1 - (
            summary["weighted_net_cost_per_task"] / baseline_cost
        )


def build_threshold_summary(year_summaries, events):
    year_points = {item["year"]: item for item in year_summaries}
    inflation_windows = build_context_windows(
        detect_threshold_runs(
            [(item["year"], item["weighted_orchestration_inflation_factor"]) for item in year_summaries],
            ORCHESTRATION_INFLATION_THRESHOLD,
        )[1],
        prefix="Inflation window",
    )
    cache_windows = build_context_windows(
        detect_threshold_runs(
            [(item["year"], item["weighted_cached_discount_ratio"]) for item in year_summaries],
            CACHED_DISCOUNT_THRESHOLD,
        )[1],
        prefix="Cache window",
    )
    decline_windows = build_context_windows(
        detect_threshold_runs(
            [(item["year"], item["cost_decline_vs_baseline"]) for item in year_summaries],
            COST_DECLINE_THRESHOLD,
        )[1],
        prefix="Cost decline window",
    )

    event_context = [
        ContextEvent(
            year=item["event_year"],
            event_type=item["event_type"],
            event_name=item["event_name"],
            description=item["description"],
            source_url=item["source_url"],
        )
        for item in events
    ]
    inflation_event_matches = match_events_to_windows(
        event_context,
        inflation_windows,
        years_before=1,
        years_after=0,
    )

    return {
        "inflation_windows": inflation_windows,
        "cache_windows": cache_windows,
        "decline_windows": decline_windows,
        "inflation_event_matches": inflation_event_matches,
        "latest_year": year_summaries[-1]["year"],
        "latest_inflation": year_summaries[-1]["weighted_orchestration_inflation_factor"],
        "latest_cache_discount": year_summaries[-1]["weighted_cached_discount_ratio"],
        "latest_cost_decline": year_summaries[-1]["cost_decline_vs_baseline"],
        "latest_cost_per_task": year_summaries[-1]["weighted_net_cost_per_task"],
        "latest_tokens_per_task": year_summaries[-1]["weighted_tokens_per_task"],
        "baseline_cost_per_task": year_summaries[0]["weighted_net_cost_per_task"],
        "baseline_tokens_per_task": year_summaries[0]["weighted_tokens_per_task"],
        "year_points": year_points,
    }


def interpret(year_summaries, comparison, threshold_summary):
    price_start = year_summaries[0]["blended_token_price_per_1m_usd"]
    price_end = year_summaries[-1]["blended_token_price_per_1m_usd"]
    usage_start = year_summaries[0]["weighted_tokens_per_task"]
    usage_end = year_summaries[-1]["weighted_tokens_per_task"]
    cost_start = year_summaries[0]["weighted_net_cost_per_task"]
    cost_end = year_summaries[-1]["weighted_net_cost_per_task"]

    if cost_end <= cost_start * 0.5 and threshold_summary["latest_inflation"] >= ORCHESTRATION_INFLATION_THRESHOLD:
        verdict = (
            "Cheaper tokens still reduce cost per task overall, but multi-step orchestration absorbs a meaningful share of the savings."
        )
    elif cost_end >= cost_start:
        verdict = (
            "Orchestration inflation fully offsets lower token prices in this scenario, so the workflow does not get cheaper per task."
        )
    else:
        verdict = (
            "Lower token prices and higher token usage pull in opposite directions, leaving a mixed workflow-level outcome."
        )

    inflation_windows = threshold_summary["inflation_windows"]
    cache_windows = threshold_summary["cache_windows"]
    decline_windows = threshold_summary["decline_windows"]
    event_text = "; ".join(
        f"{item.event.year} {item.event.event_name} ({item.timing})"
        for item in threshold_summary["inflation_event_matches"]
    ) or "No inflation-window event matches were found."

    return (
        f"Blended list prices fell from {format_currency(price_start)} to {format_currency(price_end)} per 1M tokens, while weighted tokens per task rose from {usage_start:,.0f} to {usage_end:,.0f}. "
        f"The signal comparison is {comparison['relationship']}: {comparison['explanation']} "
        f"Net cost per task moved from {format_currency(cost_start)} to {format_currency(cost_end)}. {verdict} "
        f"Inflation threshold windows: {len(inflation_windows)}; cache windows: {len(cache_windows)}; cost-decline windows: {len(decline_windows)}. "
        f"Relevant event context around inflation windows: {event_text}"
    )


def write_scenario_outputs(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "year",
        "task_type",
        "task_name",
        "pattern_id",
        "pattern_name",
        "model_family",
        "vendor",
        "model",
        "scenario_share",
        "baseline_total_tokens",
        "gross_input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "total_tokens",
        "orchestration_inflation_factor",
        "cached_discount_ratio",
        "gross_cost_per_task",
        "net_cost_per_task",
        "selected_input_per_1m_usd",
        "selected_output_per_1m_usd",
        "selected_cached_input_per_1m_usd",
        "selected_context_window_tokens",
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_csv(year_summaries, comparison, threshold_summary, interpretation, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {"metric": "title", "value": TITLE},
        {"metric": "question", "value": QUESTION},
        {"metric": "price_trend_direction", "value": comparison["signal_a_direction"]},
        {"metric": "usage_trend_direction", "value": comparison["signal_b_direction"]},
        {"metric": "signal_relationship", "value": comparison["relationship"]},
        {"metric": "latest_orchestration_inflation_factor", "value": f"{threshold_summary['latest_inflation']:.4f}"},
        {"metric": "latest_cached_discount_ratio", "value": f"{threshold_summary['latest_cache_discount']:.4f}"},
        {"metric": "latest_cost_decline_vs_baseline", "value": f"{threshold_summary['latest_cost_decline']:.4f}"},
        {"metric": "inflation_windows", "value": ", ".join(
            f"{window.name} {window.start}-{window.end}" for window in threshold_summary["inflation_windows"]
        ) or "none"},
        {"metric": "cache_windows", "value": ", ".join(
            f"{window.name} {window.start}-{window.end}" for window in threshold_summary["cache_windows"]
        ) or "none"},
        {"metric": "cost_decline_windows", "value": ", ".join(
            f"{window.name} {window.start}-{window.end}" for window in threshold_summary["decline_windows"]
        ) or "none"},
        {"metric": "interpretation", "value": interpretation},
    ]
    for summary in year_summaries:
        rows.extend(
            [
                {"metric": f"{summary['year']}_blended_token_price_per_1m_usd", "value": f"{summary['blended_token_price_per_1m_usd']:.4f}"},
                {"metric": f"{summary['year']}_weighted_tokens_per_task", "value": f"{summary['weighted_tokens_per_task']:.2f}"},
                {"metric": f"{summary['year']}_weighted_net_cost_per_task", "value": f"{summary['weighted_net_cost_per_task']:.4f}"},
            ]
        )

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerows(rows)


def annotate_events(ax, events, y_position, *, show_labels=False):
    for index, event in enumerate(events):
        x_position = year_fraction(event["event_date"])
        ax.axvline(x_position, color="#7a6c5d", linewidth=1.0, alpha=0.18)
        if show_labels:
            ax.text(
                x_position,
                y_position,
                event["event_name"],
                rotation=90,
                va="top",
                ha="right",
                fontsize=7,
                color="#4b4035",
                alpha=0.85,
            )


def annotate_threshold(ax, y_value, label, color, *, vertical_offset=0.0):
    x_min, x_max = ax.get_xlim()
    x_position = x_max - ((x_max - x_min) * 0.01)
    ax.text(
        x_position,
        y_value + vertical_offset,
        label,
        ha="right",
        va="bottom",
        fontsize=8,
        color=color,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 1.5},
    )


def build_chart(year_summaries, events, path):
    years = [item["year"] for item in year_summaries]
    input_prices = [item["blended_input_price_per_1m_usd"] for item in year_summaries]
    output_prices = [item["blended_output_price_per_1m_usd"] for item in year_summaries]
    baseline_tokens = [item["weighted_baseline_tokens_per_task"] for item in year_summaries]
    total_tokens = [item["weighted_tokens_per_task"] for item in year_summaries]
    inflation = [item["weighted_orchestration_inflation_factor"] for item in year_summaries]
    cache_ratio = [item["weighted_cached_discount_ratio"] for item in year_summaries]
    gross_cost = [item["weighted_gross_cost_per_task"] for item in year_summaries]
    net_cost = [item["weighted_net_cost_per_task"] for item in year_summaries]

    plt.style.use("default")
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True)
    fig.suptitle(TITLE, fontsize=14, y=0.98)

    price_ax = axes[0][0]
    usage_ax = axes[0][1]
    inflation_ax = axes[1][0]
    cost_ax = axes[1][1]

    price_ax.plot(years, input_prices, marker="o", linewidth=2.4, color="#0f766e", label="Estimated blended input list price / 1M")
    price_ax.plot(years, output_prices, marker="o", linewidth=2.4, color="#be123c", label="Estimated blended output list price / 1M")
    price_ax.set_title("Declining Estimated Token List Price Trends")
    price_ax.set_ylabel("USD per 1M tokens")
    price_ax.grid(axis="y", alpha=0.25)
    price_ax.legend(frameon=False)

    usage_ax.plot(years, baseline_tokens, marker="o", linewidth=2.2, color="#64748b", label="Estimated single-pass baseline tokens / task")
    usage_ax.plot(years, total_tokens, marker="o", linewidth=2.4, color="#1d4ed8", label="Estimated total workflow tokens / task")
    usage_ax.set_title("Rising Estimated Token Usage per Task")
    usage_ax.set_ylabel("Tokens per task")
    usage_ax.grid(axis="y", alpha=0.25)
    usage_ax.legend(frameon=False)

    inflation_ax.plot(years, inflation, marker="o", linewidth=2.4, color="#92400e", label="Estimated orchestration inflation factor")
    inflation_ax.plot(years, cache_ratio, marker="o", linewidth=2.0, color="#15803d", label="Estimated cached discount ratio")
    inflation_ax.axhline(ORCHESTRATION_INFLATION_THRESHOLD, color="#92400e", linestyle="--", alpha=0.6)
    inflation_ax.axhline(CACHED_DISCOUNT_THRESHOLD, color="#15803d", linestyle=":", alpha=0.8)
    inflation_ax.set_title("Rising Orchestration Inflation vs. Cache Efficiency")
    inflation_ax.set_ylabel("Ratio")
    inflation_ax.grid(axis="y", alpha=0.25)
    inflation_ax.legend(frameon=False, loc="upper left")

    cost_ax.plot(years, gross_cost, marker="o", linewidth=2.2, color="#7c3aed", label="Estimated gross workflow cost / task")
    cost_ax.plot(years, net_cost, marker="o", linewidth=2.4, color="#111827", label="Estimated net workflow cost / task after cache")
    cost_ax.axhline(net_cost[0] * (1 - COST_DECLINE_THRESHOLD), color="#111827", linestyle="--", alpha=0.5)
    cost_ax.set_title("Estimated Task Cost After Cache Savings")
    cost_ax.set_ylabel("USD per task")
    cost_ax.grid(axis="y", alpha=0.25)
    cost_ax.legend(frameon=False)

    for ax in axes.flat:
        annotate_events(ax, events, ax.get_ylim()[1], show_labels=False)
        ax.set_xticks(years)
        ax.set_xlim(years[0] - 0.1, years[-1] + 0.1)
        ax.set_xlabel("Year")

    annotate_events(price_ax, events, price_ax.get_ylim()[1] * 0.98, show_labels=True)
    annotate_events(inflation_ax, events, inflation_ax.get_ylim()[1] * 0.98, show_labels=True)
    annotate_threshold(
        inflation_ax,
        ORCHESTRATION_INFLATION_THRESHOLD,
        "Attention threshold: estimated inflation >= 3.0x",
        "#92400e",
        vertical_offset=0.08,
    )
    annotate_threshold(
        inflation_ax,
        CACHED_DISCOUNT_THRESHOLD,
        "High cache-efficiency threshold: estimated cache discount >= 80%",
        "#15803d",
        vertical_offset=0.08,
    )
    annotate_threshold(
        cost_ax,
        net_cost[0] * (1 - COST_DECLINE_THRESHOLD),
        "Major savings threshold: estimated net cost <= 50% of 2023 baseline",
        "#111827",
        vertical_offset=max(net_cost) * 0.02,
    )

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def build_console_report(year_summaries, comparison, threshold_summary, interpretation):
    inflation_windows = ", ".join(
        f"{window.name} {window.start}-{window.end} ({format_duration(window.duration)})"
        for window in threshold_summary["inflation_windows"]
    ) or "none"
    cache_windows = ", ".join(
        f"{window.name} {window.start}-{window.end} ({format_duration(window.duration)})"
        for window in threshold_summary["cache_windows"]
    ) or "none"
    decline_windows = ", ".join(
        f"{window.name} {window.start}-{window.end} ({format_duration(window.duration)})"
        for window in threshold_summary["decline_windows"]
    ) or "none"

    return "\n".join(
        [
            TITLE,
            "-" * len(TITLE),
            f"Question: {QUESTION}",
            f"Price trend direction: {comparison['signal_a_direction']}",
            f"Usage trend direction: {comparison['signal_b_direction']}",
            f"Relationship: {comparison['relationship']}",
            f"Latest orchestration inflation factor: {format_ratio(threshold_summary['latest_inflation'])}",
            f"Latest cached discount ratio: {format_percent(threshold_summary['latest_cache_discount'])}",
            f"Latest cost decline vs baseline: {format_percent(threshold_summary['latest_cost_decline'])}",
            f"Inflation windows: {inflation_windows}",
            f"Cache windows: {cache_windows}",
            f"Cost decline windows: {decline_windows}",
            "",
            "Interpretation:",
            interpretation,
            "",
            f"Scenario output: {SCENARIOS_PATH.relative_to(REPO_ROOT).as_posix()}",
            f"Summary output: {SUMMARY_PATH.relative_to(REPO_ROOT).as_posix()}",
            f"Chart output: {CHART_PATH.relative_to(REPO_ROOT).as_posix()}",
        ]
    )


def main():
    pricing_rows = load_vendor_pricing(PRICING_PATH)
    task_profiles = load_task_profiles(TASKS_PATH)
    patterns = load_patterns(PATTERNS_PATH)
    events = load_market_events(EVENTS_PATH)

    scenario_rows = []
    year_summaries = []

    for year in ANALYSIS_YEARS:
        year_rows = []
        for task in task_profiles:
            family = MODEL_FAMILY_BY_TASK[task["task_type"]]
            model = choose_market_model(pricing_rows, family, year)
            for pattern in patterns:
                year_rows.append(
                    compute_scenario_row(
                        year,
                        task,
                        pattern,
                        model,
                        REALIZED_CACHE_FACTOR_BY_YEAR[year],
                    )
                )

        scenario_rows.extend(year_rows)
        year_summaries.append(summarize_year(year, year_rows))

    attach_cost_decline(year_summaries)

    price_direction = classify_trend_direction(
        [item["blended_token_price_per_1m_usd"] for item in year_summaries]
    )
    usage_direction = classify_trend_direction(
        [item["weighted_tokens_per_task"] for item in year_summaries]
    )
    comparison = compare_signal_directions(
        price_direction,
        usage_direction,
        "Estimated blended token list price",
        "Estimated weighted tokens per task",
    )
    threshold_summary = build_threshold_summary(year_summaries, events)
    interpretation = interpret(year_summaries, comparison, threshold_summary)

    write_scenario_outputs(scenario_rows, SCENARIOS_PATH)
    write_summary_csv(year_summaries, comparison, threshold_summary, interpretation, SUMMARY_PATH)
    build_chart(year_summaries, events, CHART_PATH)

    print(build_console_report(year_summaries, comparison, threshold_summary, interpretation))


if __name__ == "__main__":
    main()