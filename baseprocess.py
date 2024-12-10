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
        
        # Load the CSV file into a DataFrame
        try:
            df = pd.read_csv(file, delimiter="\t", engine="python")
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
        
        # Convert numeric columns to proper types
        for col in df.columns:
            print(f"Processing column: {col}")
            print(f"Column type: {type(df[col])}")
            
            if isinstance(df[col], pd.Series):  # Ensure it's a Series
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert to numeric, set non-convertible values to NaN
                except Exception as e:
                    print(f"Error converting column {col} to numeric: {e}")
            else:
                print(f"Column {col} is not a Series. Skipping conversion.")
        
        # Save descriptive statistics
        summary = df.describe(include='all').T
        summary_file = f"{file}_summary.csv"
        summary.to_csv(summary_file)
        print(f"Summary statistics saved to: {summary_file}")
        
        # Generate and save visualizations
        if 'voltage_load' in df.columns and 'temperature_battery' in df.columns:
            plt.figure(figsize=(10, 6))
            sns.scatterplot(data=df, x='voltage_load', y='temperature_battery')
            plt.title(f"Voltage vs Battery Temperature - {file}")
            plot_file = f"{file}_voltage_vs_temp.png"
            plt.savefig(plot_file)
            plt.close()
            print(f"Scatterplot saved to: {plot_file}")
        
        # Identify potential outliers in 'voltage_load' (if exists)
        if 'voltage_load' in df.columns:
            q1 = df['voltage_load'].quantile(0.25)
            q3 = df['voltage_load'].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = df[(df['voltage_load'] < lower_bound) | (df['voltage_load'] > upper_bound)]
            outlier_file = f"{file}_voltage_outliers.csv"
            outliers.to_csv(outlier_file, index=False)
            print(f"Outliers saved to: {outlier_file}")
        
        print(f"Finished processing {file}\n")
    
    print("Processing completed for all files.")

if __name__ == "__main__":
    process_battery_data()
