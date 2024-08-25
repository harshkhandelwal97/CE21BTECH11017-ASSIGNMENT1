import pandas as pd
import matplotlib.pyplot as plt

def plot_min_temperatures(dates: list, csv_file: str) -> None:
    """
    Plots a graph between dates and the minimum temperature for each date from a CSV file.
    
    Parameters:
    - dates (list): A list of dates in the format 'YYYY-MM-DD'.
    - csv_file (str): The path to the CSV file containing temperature data.
    """
    try:
        # Load the CSV file into a DataFrame with 'Timestamp' parsed as datetime
        df = pd.read_csv(csv_file, parse_dates=['Timestamp'])
        
        # Ensure 'Timestamp' is in datetime format
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Set 'Timestamp' as the index
        df.set_index('Timestamp', inplace=True)
        
        # Print column names for debugging
        print("Column names in the DataFrame:")
        print(df.columns)
        
        # Ensure 'Temperature' column is present and clean any leading/trailing spaces
        temperature_col = 'Temperature'
        if temperature_col not in df.columns:
            raise ValueError(f"CSV file must contain '{temperature_col}' column.")
        
        # Group by date and find the min and max temperature
        daily_temps = df.groupby(df.index.date)[temperature_col].agg(['min', 'max'])
        
        # Rename columns for clarity
        daily_temps.columns = ['Min Temperature', 'Max Temperature']
        
        # Print the daily_temps DataFrame for debugging
        print("\nDaily Temperatures DataFrame:")
        print(daily_temps)
        
        min_temperatures = []

        for date in pd.to_datetime(dates):
            # Check if the date is in the DataFrame
            if date.date() in daily_temps.index:
                # Get the minimum temperature for the date
                min_temp = daily_temps.loc[date.date(), 'Min Temperature']
                min_temperatures.append(min_temp)
            else:
                min_temperatures.append(None)  # Append None if no data is available for the date
                print(f"No data available for the date {date.date()}.")
        
        # Plotting the results
        plt.figure(figsize=(10, 5))
        plt.plot(dates, min_temperatures, marker='o', linestyle='-', color='b')
        plt.xlabel('Date')
        plt.ylabel('Minimum Temperature')
        plt.title('Minimum Temperature by Date')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.grid(True)
        plt.show()
    
    except Exception as e:
        print(f"Error: {e}")

# Get user input for dates
def get_dates_from_user() -> list:
    """
    Prompts the user to enter dates and returns a list of dates.
    
    Returns:
    - list: A list of dates entered by the user.
    """
    try:
        num_dates = int(input("Enter the number of dates: "))
        dates = []
        
        for _ in range(num_dates):
            date = input("Enter a date (YYYY-MM-DD): ")
            dates.append(date)
        
        return dates
    except ValueError:
        print("Invalid input. Please enter numeric values for the number of dates.")
        return []

# Example usage
csv_file = 'data.csv'  # Ensure this path is correct
dates = get_dates_from_user()
if dates:
    plot_min_temperatures(dates, csv_file)
