import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_battery_data():
    # List all CSV files in the current directory
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    
    for file in csv_files:
        print(f"Processing file: {file}")
        
        # Load the CSV file into a DataFrame
        try:
            df = pd.read_csv(file)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            continue
        
        # Basic data exploration
        print(f"First 5 rows of {file}:")
        print(df.head())
        
        # Clean the data
        df.dropna(how='all', axis=1, inplace=True)  # Drop empty columns
        df.dropna(how='all', axis=0, inplace=True)  # Drop empty rows
        df.columns = [col.strip().lower() for col in df.columns]  # Clean column names
        
        # Check if 'relative_time' exists in the data
        if 'time' not in df.columns:
            print(f"'time' column is missing in {file}. Skipping this file.")
            continue
        
        # Convert relevant columns to proper data types
        df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
        df['time'] = pd.to_numeric(df['time'], errors='coerce')
        df['voltage_charger'] = pd.to_numeric(df['voltage_charger'], errors='coerce')
        df['temperature_battery'] = pd.to_numeric(df['temperature_battery'], errors='coerce')
        df['voltage_load'] = pd.to_numeric(df['voltage_load'], errors='coerce')
        df['current_load'] = pd.to_numeric(df['current_load'], errors='coerce')
        df['temperature_mosfet'] = pd.to_numeric(df['temperature_mosfet'], errors='coerce')
        df['temperature_resistor'] = pd.to_numeric(df['temperature_resistor'], errors='coerce')
        df['mission_type'] = pd.to_numeric(df['mission_type'], errors='coerce')
        
        # Group the data by mode (-1 = discharge, 0 = rest, 1 = charge)
        discharge_data = df[df['mode'] == -1]
        rest_data = df[df['mode'] == 0]
        charge_data = df[df['mode'] == 1]
        
        # Perform analysis for discharge mode
        if not discharge_data.empty:
            print(f"Analyzing discharge mode for {file}...")
            discharge_stats = discharge_data[['voltage_load', 'current_load', 'temperature_mosfet', 'temperature_resistor']].describe()
            print(f"Discharge statistics for {file}:")
            print(discharge_stats)
            discharge_stats.to_csv(f"{file}_discharge_stats.csv")
            
            # Plot voltage vs current for discharge
            plt.figure(figsize=(10, 6))
            sns.scatterplot(data=discharge_data, x='voltage_load', y='current_load')
            plt.title(f"Voltage vs Current (Discharge) - {file}")
            plt.xlabel("Voltage (V)")
            plt.ylabel("Current (A)")
            plt.savefig(f"{file}_voltage_vs_current_discharge.png")
            plt.close()
        
        # Perform analysis for rest mode
        if not rest_data.empty:
            print(f"Analyzing rest mode for {file}...")
            rest_stats = rest_data[['voltage_charger', 'temperature_battery']].describe()
            print(f"Rest statistics for {file}:")
            print(rest_stats)
            rest_stats.to_csv(f"{file}_rest_stats.csv")
            
            # Plot temperature during rest mode
            plt.figure(figsize=(10, 6))
            sns.lineplot(data=rest_data, x='time', y='temperature_battery')
            plt.title(f"Temperature vs Time (Rest) - {file}")
            plt.xlabel("Time (s)")
            plt.ylabel("Temperature (°C)")
            plt.savefig(f"{file}_temperature_vs_time_rest.png")
            plt.close()
        
        # Perform analysis for charge mode
        if not charge_data.empty:
            print(f"Analyzing charge mode for {file}...")
            charge_stats = charge_data[['voltage_charger', 'temperature_battery']].describe()
            print(f"Charge statistics for {file}:")
            print(charge_stats)
            charge_stats.to_csv(f"{file}_charge_stats.csv")
            
            # Plot charger voltage vs battery temperature during charge
            plt.figure(figsize=(10, 6))
            sns.lineplot(data=charge_data, x='time', y='voltage_charger', label='Charger Voltage')
            sns.lineplot(data=charge_data, x='time', y='temperature_battery', label='Battery Temperature')
            plt.title(f"Voltage and Temperature vs Time (Charge) - {file}")
            plt.xlabel("Time (s)")
            plt.ylabel("Voltage (V) / Temperature (°C)")
            plt.legend()
            plt.savefig(f"{file}_voltage_temp_vs_time_charge.png")
            plt.close()

        # Overall life cycle analysis based on modes
        print(f"Overall battery cycle analysis for {file}...")
        cycle_data = df.groupby('mode').agg(
            start_time=('start_time', 'first'),
            end_time=('time', 'last'),
            average_voltage_charger=('voltage_charger', 'mean'),
            average_temperature_battery=('temperature_battery', 'mean'),
            average_voltage_load=('voltage_load', 'mean'),
            average_current_load=('current_load', 'mean')
        ).reset_index()
        print(cycle_data)
        cycle_data.to_csv(f"{file}_battery_cycle_analysis.csv", index=False)

        print(f"Finished processing {file}\n")
    
    print("Processing completed for all files.")

if __name__ == "__main__":
    analyze_battery_data()
