# SSA Agricultural Capital Pressure

This example extends the repository from threshold detection into contextual event analysis.

```text
data -> threshold windows -> event context -> interpretation
```

## Question

When imported-food pressure crosses an attention threshold in Sub-Saharan Africa, which contextual events and capital-cost conditions help explain what was happening around that period?

## Framing

This is a descriptive systems example for Sub-Saharan Africa.

It does not claim that any event caused the threshold crossing. The point is to show how a small, explicit event list and a financing proxy can make threshold windows easier to interpret.

## Data

The example reuses the existing regional agriculture dataset from the earlier threshold example and adds two local files in this folder:

- `data/ssa_capital_cost_proxy.csv`: a transparent capital-cost proxy built as the annual average of World Bank lending-rate series for Nigeria, South Africa, and Kenya
- `data/contextual_events.csv`: a small curated set of events that occurred shortly before or during the pressure windows

The imported-food-share proxy is recalculated as:

```text
estimated_food_imports = merchandise_imports * food_import_share
imported_food_share = estimated_food_imports / (agriculture_value_added + estimated_food_imports)
```

## What It Does

- loads the existing Sub-Saharan Africa agriculture system pressure dataset
- recalculates estimated food imports and the imported-food-share proxy
- loads a simple capital-cost proxy trend for regional financing conditions
- plots population on the agriculture/imports chart using a second axis for scale context
- detects years above the 15% threshold and converts them into named pressure windows
- loads a small contextual events CSV and classifies events as before or during each window
- overlays events on the imported-share chart while placing the capital-cost proxy on the second axis of that same panel
- writes a plain-language summary that adds context without claiming causation

## Recent Watch Narrative

The example now also checks whether the latest rebound is strong enough to merit a lighter watch threshold below the main 15% line. In the current data, 2024 does not create a new pressure window, but it is strong enough to discuss as a renewed watch year alongside a recent macro or trade backdrop.

## Why The Capital-Cost Proxy Is Limited

The capital-cost line is not a direct measure of agricultural borrowing costs across all of Sub-Saharan Africa. It is a transparent three-country proxy intended to add financing context to the threshold windows. That limitation is stated in the output so the example stays honest about what the line means.

## How To Run

From the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 examples/ssa_agricultural_capital_pressure/ssa_agricultural_capital_pressure.py
```

## Outputs

The script prints a console summary and creates two files in this folder:

- `ssa_agricultural_capital_pressure_summary.txt`
- `ssa_agricultural_capital_pressure.png`