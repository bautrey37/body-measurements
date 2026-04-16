import json
import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MIN_POINTS = 4
DEFAULT_HEIGHT_M = 1.75
USERS_FILE = os.path.join("data", "users.json")

TIMEFRAME_DIRS = {
    "absolute": "combined",
    "1year": "1year",
    "2year": "2year",
}


def _output_dir(user, output_suffix):
    subdir = TIMEFRAME_DIRS.get(output_suffix, output_suffix)
    path = os.path.join("out", user, subdir)
    os.makedirs(path, exist_ok=True)
    return path


def _user_from_filename(filename):
    stem = os.path.splitext(os.path.basename(filename))[0]
    if " - " in stem:
        return stem.rsplit(" - ", 1)[-1].strip()
    return stem.strip()


def create_weight_waist_graph(df, user, date_col, type_col, value_col, timeframe_name, output_suffix, start_date=None, end_date=None):
    """Dual-axis graph overlaying Weight (kg) and Waist (cm) for a timeframe."""
    filtered_df = df.copy()
    if start_date is not None:
        filtered_df = filtered_df[filtered_df[date_col] >= start_date]
    if end_date is not None:
        filtered_df = filtered_df[filtered_df[date_col] <= end_date]

    weight = filtered_df[filtered_df[type_col] == "Weight"].sort_values(date_col)
    waist = filtered_df[filtered_df[type_col] == "Waist"].sort_values(date_col)

    if len(weight) < MIN_POINTS or len(waist) < MIN_POINTS:
        print(f"Skipping Weight+Waist {timeframe_name} - need >= {MIN_POINTS} points for both "
              f"(weight={len(weight)}, waist={len(waist)})")
        return

    fig, ax_w = plt.subplots(figsize=(12, 6))
    ax_c = ax_w.twinx()

    weight_color = "#1f77b4"
    waist_color = "#d62728"

    ax_w.plot(weight[date_col], weight[value_col], marker="o", linewidth=2,
              markersize=4, color=weight_color, label="Weight (kg)")
    ax_c.plot(waist[date_col], waist[value_col], marker="s", linewidth=2,
              markersize=4, color=waist_color, label="Waist (cm)")

    ax_w.set_xlabel("Date")
    ax_w.set_ylabel("Weight (kg)", color=weight_color)
    ax_c.set_ylabel("Waist (cm)", color=waist_color)
    ax_w.tick_params(axis="y", labelcolor=weight_color)
    ax_c.tick_params(axis="y", labelcolor=waist_color)
    ax_w.grid(True, alpha=0.3)
    plt.setp(ax_w.get_xticklabels(), rotation=45, ha="right")

    lines, labels = ax_w.get_legend_handles_labels()
    lines2, labels2 = ax_c.get_legend_handles_labels()
    ax_w.legend(lines + lines2, labels + labels2, loc="best")

    plt.title(f"{user} - Weight & Waist - {timeframe_name}", fontsize=16, fontweight="bold")
    plt.tight_layout()

    output_file = os.path.join(_output_dir(user, output_suffix), f"Weight_Waist_{output_suffix}.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"Weight+Waist {timeframe_name} graph saved to: {output_file}")
    plt.close()


def create_bmi_graph(df, user, height_m, date_col, type_col, value_col, timeframe_name, output_suffix, start_date=None, end_date=None):
    """BMI over time computed from Weight (kg) and height_m, with BMI category thresholds."""
    filtered_df = df.copy()
    if start_date is not None:
        filtered_df = filtered_df[filtered_df[date_col] >= start_date]
    if end_date is not None:
        filtered_df = filtered_df[filtered_df[date_col] <= end_date]

    weight = filtered_df[filtered_df[type_col] == "Weight"].sort_values(date_col)
    if len(weight) < MIN_POINTS:
        print(f"Skipping BMI {timeframe_name} - only {len(weight)} Weight points (< {MIN_POINTS})")
        return

    bmi = weight[value_col] / (height_m ** 2)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(weight[date_col], bmi, marker="o", linewidth=2, markersize=4,
            color="#2ca02c", label="BMI")

    y_min = min(bmi.min(), 17)
    y_max = max(bmi.max(), 31)
    ax.set_ylim(y_min - 1, y_max + 1)

    ax.axhspan(min(y_min - 1, 17), 18.5, color="#1f77b4", alpha=0.2, label="Underweight (<18.5)")
    ax.axhspan(25, 30, color="#ffb347", alpha=0.2, label="Overweight (25-30)")
    ax.axhspan(30, max(y_max + 1, 40), color="#d62728", alpha=0.2, label="Obese (30+)")
    ax.axhline(18.5, color="#1f77b4", linestyle="--", linewidth=1)
    ax.axhline(25, color="#ff7f0e", linestyle="--", linewidth=1)
    ax.axhline(30, color="#d62728", linestyle="--", linewidth=1.5)
    ax.text(weight[date_col].iloc[0], 30.2, "Obese threshold (30)",
            color="#d62728", fontsize=10, fontweight="bold", va="bottom")
    ax.text(weight[date_col].iloc[0], 25.2, "Overweight threshold (25)",
            color="#ff7f0e", fontsize=9, va="bottom")
    ax.text(weight[date_col].iloc[0], 18.7, "Underweight threshold (18.5)",
            color="#1f77b4", fontsize=9, va="bottom")

    latest_bmi = bmi.iloc[-1]
    if latest_bmi >= 30:
        status = f"WARNING: Latest BMI {latest_bmi:.1f} - Obese"
        status_color = "#d62728"
    elif latest_bmi >= 25:
        status = f"Latest BMI {latest_bmi:.1f} - Overweight"
        status_color = "#ff7f0e"
    elif latest_bmi < 18.5:
        status = f"WARNING: Latest BMI {latest_bmi:.1f} - Underweight"
        status_color = "#1f77b4"
    else:
        status = f"Latest BMI {latest_bmi:.1f}"
        status_color = "#2ca02c"
    ax.set_title(f"{user} - BMI - {timeframe_name}\n{status}", fontsize=15, fontweight="bold",
                 color=status_color)
    ax.set_xlabel("Date")
    ax.set_ylabel("BMI (kg/m²)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    plt.tight_layout()

    output_file = os.path.join(_output_dir(user, output_suffix), f"BMI_{output_suffix}.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"BMI {timeframe_name} graph saved to: {output_file}")
    plt.close()


def create_timeframe_graphs(df, user, date_col, type_col, value_col, unique_types, timeframe_name, output_suffix, start_date=None, end_date=None):
    """Create graphs for a specific timeframe"""

    # Filter data by timeframe if specified
    filtered_df = df.copy()
    if start_date is not None:
        filtered_df = filtered_df[filtered_df[date_col] >= start_date]
    if end_date is not None:
        filtered_df = filtered_df[filtered_df[date_col] <= end_date]
    
    if filtered_df.empty:
        print(f"No data available for {timeframe_name} timeframe")
        return
    
    # Filter out types with fewer than MIN_POINTS data points in this timeframe
    types_with_data = []
    for data_type in unique_types:
        type_data = filtered_df[filtered_df[type_col] == data_type]
        if len(type_data) >= MIN_POINTS:
            types_with_data.append(data_type)
        else:
            print(f"Skipping {data_type} - {len(type_data)} points (< {MIN_POINTS}) in {timeframe_name} timeframe")

    if not types_with_data:
        print(f"No types have enough data for {timeframe_name} timeframe")
        return
    
    unique_types = types_with_data
    
    # Determine time range for this timeframe
    if pd.api.types.is_datetime64_any_dtype(filtered_df[date_col]):
        min_date = filtered_df[date_col].min()
        max_date = filtered_df[date_col].max()
        print(f"{timeframe_name} date range: {min_date} to {max_date}")
    else:
        min_date = filtered_df[date_col].min()
        max_date = filtered_df[date_col].max()
    
    # Create subplot layout
    num_types = len(unique_types)
    cols = 2 if num_types > 1 else 1
    rows = (num_types + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    fig.suptitle(f'{user} - Data Analysis by Type - {timeframe_name}', fontsize=16, y=0.98)
    
    # If only one subplot, axes might not be an array
    if num_types == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes if isinstance(axes, np.ndarray) else [axes]
    else:
        axes = axes.flatten()
    
    # Create a graph for each type
    for i, data_type in enumerate(unique_types):
        ax = axes[i] if i < len(axes) else plt.subplot(rows, cols, i + 1)
        
        # Filter data for this type and timeframe
        type_data = filtered_df[filtered_df[type_col] == data_type].copy()
        type_data = type_data.sort_values(date_col)
        
        if not type_data.empty:
            # Plot the data
            ax.plot(type_data[date_col], type_data[value_col], marker='o', linewidth=2, markersize=4)
            ax.set_title(f'{data_type} - {timeframe_name}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Time')
            ax.set_ylabel('Value')
            ax.grid(True, alpha=0.3)
            
            # Set timeframe limits
            if pd.api.types.is_datetime64_any_dtype(filtered_df[date_col]):
                ax.set_xlim(min_date, max_date)
            else:
                ax.set_xlim(min_date, max_date)
            
            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        else:
            ax.text(0.5, 0.5, f'No data for {data_type}\nin {timeframe_name}', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f'{data_type} - {timeframe_name}', fontsize=14, fontweight='bold')
    
    # Hide any unused subplots
    for i in range(num_types, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    
    # Save the combined graph
    output_file = os.path.join(_output_dir(user, output_suffix), f'data_graphs_combined_{output_suffix}.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Combined {timeframe_name} graphs saved to: {output_file}")
    
    # Also create individual graphs for each type (only for types with data)
    for data_type in unique_types:
        plt.figure(figsize=(10, 6))
        
        # Filter data for this type and timeframe
        type_data = filtered_df[filtered_df[type_col] == data_type].copy()
        type_data = type_data.sort_values(date_col)
        
        # Plot the data (we know this type has data since we filtered above)
        plt.plot(type_data[date_col], type_data[value_col], marker='o', linewidth=2, markersize=6)
        plt.title(f'{data_type} Over Time - {timeframe_name}', fontsize=16, fontweight='bold')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.grid(True, alpha=0.3)
        
        # Set timeframe limits
        if pd.api.types.is_datetime64_any_dtype(filtered_df[date_col]):
            plt.xlim(min_date, max_date)
        else:
            plt.xlim(min_date, max_date)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save individual graph
        safe_filename = data_type.replace(' ', '_').replace('/', '_').replace('\\', '_')
        individual_file = os.path.join(_output_dir(user, output_suffix), f'{safe_filename}_graph_{output_suffix}.png')
        plt.savefig(individual_file, dpi=300, bbox_inches='tight')
        print(f"Individual {timeframe_name} graph for {data_type} saved to: {individual_file}")
        
        plt.close()

def _load_users():
    """Load per-user info (e.g., height_m) from data/users.json. Missing file → empty dict."""
    if not os.path.exists(USERS_FILE):
        print(f"No users file at {USERS_FILE}; using defaults")
        return {}
    with open(USERS_FILE) as f:
        return json.load(f)


def _detect_columns(df):
    date_col = type_col = value_col = None
    for col in df.columns:
        lc = col.lower()
        if date_col is None and any(k in lc for k in ("date", "time", "timestamp")):
            date_col = col
        if type_col is None and any(k in lc for k in ("type", "category", "kind")):
            type_col = col
        if value_col is None and any(k in lc for k in ("value", "amount", "measurement", "data")):
            value_col = col

    if not date_col and len(df.columns) >= 1:
        date_col = df.columns[0]
    if not type_col and len(df.columns) >= 2:
        type_col = df.columns[1] if len(df.columns) > 2 else df.columns[-1]
    if not value_col and len(df.columns) >= 2:
        value_col = df.columns[-1] if len(df.columns) > 2 else df.columns[1]
    return date_col, type_col, value_col


def _process_csv(csv_file, users):
    user = _user_from_filename(csv_file)
    info = users.get(user, {})
    height_m = info.get("height_m", DEFAULT_HEIGHT_M)
    gender = info.get("gender", "unspecified")
    print(f"\n########## Processing {csv_file} (user={user}, height={height_m}m, gender={gender}) ##########")

    df = pd.read_csv(csv_file)
    date_col, type_col, value_col = _detect_columns(df)
    print(f"Using columns - Date: {date_col}, Type: {type_col}, Value: {value_col}")

    try:
        df[date_col] = pd.to_datetime(df[date_col])
    except Exception:
        print(f"Could not convert {date_col} to datetime, using as-is")

    unique_types = df[type_col].unique()

    print("\n=== Creating absolute timeframe graphs ===")
    create_timeframe_graphs(df, user, date_col, type_col, value_col, unique_types,
                            "All Time", "absolute")
    create_weight_waist_graph(df, user, date_col, type_col, value_col,
                              "All Time", "absolute")
    create_bmi_graph(df, user, height_m, date_col, type_col, value_col,
                     "All Time", "absolute")

    if pd.api.types.is_datetime64_any_dtype(df[date_col]):
        max_date = df[date_col].max()

        print("\n=== Creating 1-year timeframe graphs ===")
        one_year_ago = max_date - timedelta(days=365)
        create_timeframe_graphs(df, user, date_col, type_col, value_col, unique_types,
                                "Last 1 Year", "1year", start_date=one_year_ago)
        create_weight_waist_graph(df, user, date_col, type_col, value_col,
                                  "Last 1 Year", "1year", start_date=one_year_ago)
        create_bmi_graph(df, user, height_m, date_col, type_col, value_col,
                         "Last 1 Year", "1year", start_date=one_year_ago)

        print("\n=== Creating 2-year timeframe graphs ===")
        two_years_ago = max_date - timedelta(days=730)
        create_timeframe_graphs(df, user, date_col, type_col, value_col, unique_types,
                                "Last 2 Years", "2year", start_date=two_years_ago)
        create_weight_waist_graph(df, user, date_col, type_col, value_col,
                                  "Last 2 Years", "2year", start_date=two_years_ago)
        create_bmi_graph(df, user, height_m, date_col, type_col, value_col,
                         "Last 2 Years", "2year", start_date=two_years_ago)
    else:
        print("Date column is not datetime format, cannot create year-based timeframe graphs")


def create_graphs():
    os.makedirs("out", exist_ok=True)

    data_files = sorted(f for f in os.listdir("data") if f.endswith(".csv"))
    if not data_files:
        print("No CSV files found in data folder")
        return

    users = _load_users()
    for name in data_files:
        _process_csv(os.path.join("data", name), users)


if __name__ == "__main__":
    create_graphs()
