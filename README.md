# Body Measurements Data Analysis

This project generates graphs from CSV data in the `data` folder, creating separate visualizations for each data type with aligned timeframes.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the graph generation script:
```bash
python generate_graphs.py
```

The script will:
- Read CSV files from the `data` folder
- Automatically detect date, type, and value columns
- Create separate graphs for each data type
- Align timeframes across all graphs
- Save outputs to the `out` folder

## Output

The script generates:
- `data_graphs_combined.png` - All types in a single subplot layout
- Individual graph files for each type (e.g., `weight_graph.png`)

## CSV Format

The script expects CSV files with columns containing:
- Date/time information
- Type/category information
- Value/measurement data

Column detection is automatic based on common naming patterns.
