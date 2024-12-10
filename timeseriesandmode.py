import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

def process_battery_data():
    # List all CSV files in the current directory
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    
    for file in csv_files:
        print(f"Processing file: {file}")
        
        # Load the CSV file into a DataFrame (use comma as the delimiter)
        try:
            df = pd.read_csv(file, delimiter=",", engine="python")
        except Exception as e:
            print(f"Error reading {file}: {e}")
            continue
        
        # Check the first few rows and columns
        print("First 5 rows of data:")
        print(df.head())
        print("Column names and types:")
        print(df.info())
        
        # Drop completely empty columns and rows
        df.dropna(how='all', axis=1, inplace=True)
        df.dropna(how='all', axis=0, inplace=True)
        
        # Ensure proper column parsing and standardize headers
        df.columns = [col.strip().lower() for col in df.columns]
        
        # Handle combined data in a single column issue
        if len(df.columns) == 1:
            print("Data appears to be in a single column. Attempting to split by commas.")
            df = df[df.columns[0]].str.split(',', expand=True)
            df.columns = df.iloc[0]  # Set first row as column headers
            df = df[1:]  # Drop the first row

        # Ensure the time column is in datetime format
        if 'start_time' in df.columns:
            df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
        
        # Check if the relevant columns exist for analysis
        if 'start_time' in df.columns and 'mode' in df.columns:
            # Perform time-series analysis based on 'start_time' and 'mode'
            df.set_index('start_time', inplace=True)
            # Resample by day and calculate mode, then pick the first mode if there are multiple
            df_resampled = df.resample('D').apply(lambda x: x['mode'].mode().iloc[0] if not x['mode'].mode().empty else None)
            
            # Save time-series analysis result to CSV
            ts_file = os.path.join(os.getcwd(), f"{file}_time_series_analysis.csv")
            df_resampled.to_csv(ts_file)
            print(f"Time-series analysis saved to: {ts_file}")
            
            # Plot the time-series analysis
            plt.figure(figsize=(10, 6))
            df_resampled.plot()
            plt.title(f"Mode of Battery Mode Over Time - {file}")
            plt.xlabel('Date')
            plt.ylabel('Mode')
            ts_plot_file = os.path.join(os.getcwd(), f"{file}_time_series_analysis.png")
            plt.savefig(ts_plot_file)
            plt.close()
            print(f"Time-series plot saved to: {ts_plot_file}")
        
        print(f"Finished processing {file}\n")
    
    print("Processing completed for all files.")

if __name__ == "__main__":
    process_battery_data()
