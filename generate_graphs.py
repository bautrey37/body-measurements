import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import numpy as np

def create_graphs():
    # Ensure output directory exists
    os.makedirs('out', exist_ok=True)
    
    # Find CSV file in data folder
    data_files = [f for f in os.listdir('data') if f.endswith('.csv')]
    if not data_files:
        print("No CSV files found in data folder")
        return
    
    # Use the first CSV file found
    csv_file = os.path.join('data', data_files[0])
    print(f"Processing file: {csv_file}")
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Assume the CSV has columns like 'date', 'type', 'value' or similar
    # Try to identify date and type columns
    date_col = None
    type_col = None
    value_col = None
    
    # Look for common date column names
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp']):
            date_col = col
            break
    
    # Look for type column
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['type', 'category', 'kind']):
            type_col = col
            break
    
    # Look for value column
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['value', 'amount', 'measurement', 'data']):
            value_col = col
            break
    
    # If not found, use column positions (assuming standard format)
    if not date_col and len(df.columns) >= 1:
        date_col = df.columns[0]
    if not type_col and len(df.columns) >= 2:
        type_col = df.columns[1] if len(df.columns) > 2 else df.columns[-1]
    if not value_col and len(df.columns) >= 2:
        value_col = df.columns[-1] if len(df.columns) > 2 else df.columns[1]
    
    print(f"Using columns - Date: {date_col}, Type: {type_col}, Value: {value_col}")
    
    # Convert date column to datetime
    try:
        df[date_col] = pd.to_datetime(df[date_col])
    except:
        print(f"Could not convert {date_col} to datetime, using as-is")
    
    # Get unique types
    unique_types = df[type_col].unique()
    print(f"Found types: {unique_types}")
    
    # Determine overall time range for alignment
    if pd.api.types.is_datetime64_any_dtype(df[date_col]):
        min_date = df[date_col].min()
        max_date = df[date_col].max()
        print(f"Date range: {min_date} to {max_date}")
    else:
        min_date = df[date_col].min()
        max_date = df[date_col].max()
    
    # Create subplot layout
    num_types = len(unique_types)
    cols = 2 if num_types > 1 else 1
    rows = (num_types + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    fig.suptitle('Data Analysis by Type', fontsize=16, y=0.98)
    
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
        
        # Filter data for this type
        type_data = df[df[type_col] == data_type].copy()
        type_data = type_data.sort_values(date_col)
        
        # Plot the data
        ax.plot(type_data[date_col], type_data[value_col], marker='o', linewidth=2, markersize=4)
        ax.set_title(f'{data_type}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.grid(True, alpha=0.3)
        
        # Align timeframes across all graphs
        if pd.api.types.is_datetime64_any_dtype(df[date_col]):
            ax.set_xlim(min_date, max_date)
        else:
            ax.set_xlim(min_date, max_date)
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    # Hide any unused subplots
    for i in range(num_types, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    
    # Save the combined graph
    output_file = os.path.join('out', 'data_graphs_combined.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Combined graphs saved to: {output_file}")
    
    # Also create individual graphs for each type
    for data_type in unique_types:
        plt.figure(figsize=(10, 6))
        
        # Filter data for this type
        type_data = df[df[type_col] == data_type].copy()
        type_data = type_data.sort_values(date_col)
        
        # Plot the data
        plt.plot(type_data[date_col], type_data[value_col], marker='o', linewidth=2, markersize=6)
        plt.title(f'{data_type} Over Time', fontsize=16, fontweight='bold')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.grid(True, alpha=0.3)
        
        # Align timeframes
        if pd.api.types.is_datetime64_any_dtype(df[date_col]):
            plt.xlim(min_date, max_date)
        else:
            plt.xlim(min_date, max_date)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save individual graph
        safe_filename = data_type.replace(' ', '_').replace('/', '_').replace('\\', '_')
        individual_file = os.path.join('out', f'{safe_filename}_graph.png')
        plt.savefig(individual_file, dpi=300, bbox_inches='tight')
        print(f"Individual graph for {data_type} saved to: {individual_file}")
        
        plt.close()

if __name__ == "__main__":
    create_graphs()
