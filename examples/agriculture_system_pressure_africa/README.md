# Agriculture System Pressure in Sub-Saharan Africa

This example extends the repository from signal comparison into threshold detection.

```text
data -> comparison -> threshold -> interpretation
```

## Question

When does imported food become a large enough share of the Sub-Saharan African food system to merit closer attention?

## Framing

This is a descriptive regional systems example focused on Sub-Saharan Africa.

It is not a forecast, not a food-security model, and not a causal claim about why conditions changed. The goal is to align two agricultural system signals, define a transparent threshold, and show when the system moves above or below that boundary.

## Dataset

The local dataset in `data/sub_saharan_africa_food_import_pressure.csv` contains annual regional observations for 2000 through 2024.

Signals used:

- `agriculture_value_added_usd`: agriculture, forestry, and fishing value added in current US$
- `food_imports_usd`: estimated food imports in current US$, calculated as merchandise imports times the food-import share
- `imported_food_share_of_supply`: a simple proxy for imported share of available supply, calculated as food imports / (agriculture value added + food imports)
- `population`: total population, included as descriptive context

Source basis:

- World Bank `NV.AGR.TOTL.CD`: Agriculture, forestry, and fishing, value added (current US$)
- World Bank `TM.VAL.MRCH.CD.WT`: Merchandise imports (current US$)
- World Bank `TM.VAL.FOOD.ZS.UN`: Food imports (% of merchandise imports)
- World Bank `SP.POP.TOTL`: Population, total

## Threshold

The default threshold is `15%` imported food share of available supply.

That means the example flags years where:

```text
food_imports_usd / (agriculture_value_added_usd + food_imports_usd) >= 15%
```

The threshold is intentionally simple and can be changed in the script.

## What It Does

- loads and aligns agricultural production and food-import signals
- calculates an imported-share proxy tied to those two signals
- detects threshold crossings and above-threshold runs
- highlights the crossings and threshold line on the chart
- writes a plain-language summary of what changed before and after the first crossing

## Domain Context

This example broadens the repository into agricultural systems and beyond the U.S. The immediate analytical focus is import dependence relative to domestic production capacity.

Related structural questions such as farm consolidation and domestic production as a share of consumption are adjacent domain signals. This example covers one tractable regional slice of that broader theme using a small public extract.

## How To Run

From the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 examples/agriculture_system_pressure_africa/agriculture_system_pressure_africa.py
```

## Outputs

The script prints a console summary and creates two files in this folder:

- `agriculture_system_pressure_africa_summary.txt`
- `agriculture_system_pressure_africa.png`