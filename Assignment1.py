import pandas as pd
import math
import sys
import matplotlib.pyplot as plt

# Read data from the CSV file
data_frame = pd.read_csv("data.csv")

# Convert the first column (Timestamp) to datetime format
data_frame['Timestamp'] = pd.to_datetime(data_frame.iloc[:, 0])

# Prompt the user for year and month input
year_selected = int(input("Enter the year (YYYY): "))
month_selected = int(input("Enter the month (MM): "))

# Function to check if the year is a leap year
def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

# Determine the number of days in the year
total_days = 366 if is_leap_year(year_selected) else 365

# Filter data for the specific month and year selected
monthly_data = data_frame[(data_frame['Timestamp'].dt.year == year_selected) & (data_frame['Timestamp'].dt.month == month_selected)]

if monthly_data.empty:
    print(f"No data available for the specified month {month_selected} and year {year_selected}.")
    sys.exit()

# Prompt user for additional required inputs
latitude_deg = float(input("Enter the latitude in degrees: "))
elevation_m = float(input("Enter the elevation above sea level in meters: "))

# Calculate the number of days in the specified month
days_in_month = pd.Period(f'{year_selected}-{month_selected:02d}', freq='M').days_in_month
date_range = pd.date_range(start=f'{year_selected}-{month_selected:02d}-01', periods=days_in_month, freq='D')

# Initialize lists to store daily values
day_indices = list(range(1, days_in_month + 1))
evapotranspiration_values = [0] * days_in_month

# Iterate through each day in the date range
for i, current_date in enumerate(date_range):
    daily_data = monthly_data[monthly_data['Timestamp'].dt.day == current_date.day]
    
    if daily_data.empty:
        continue
    
    # Extract relevant daily values
    Tmax = daily_data.iloc[:, 2].max()
    Tmin = daily_data.iloc[:, 2].min()
    RH_max = daily_data.iloc[:, 3].max()
    RH_min = daily_data.iloc[:, 3].min()
    wind_speed_avg = daily_data.iloc[:, 6].mean()
    solar_radiation_watt = daily_data.iloc[:, -1].mean()

    # Convert solar radiation from W/m² to MJ/m²/day
    solar_radiation_MJ = solar_radiation_watt * 0.0864

    # Compute mean temperature and saturation vapor pressure
    T_mean = (Tmax + Tmin) / 2
    delta_slope = 4098 * 0.6108 * math.exp((17.27 * T_mean) / (T_mean + 237.3)) / ((T_mean + 237.3) ** 2)

    # Atmospheric pressure calculation
    atmospheric_pressure = 101.3 * ((293 - 0.0065 * elevation_m) / 293) ** 5.26
    psychrometric_constant = 0.000665 * atmospheric_pressure

    # Weighting factors for the energy and aerodynamic terms
    weighting_energy = delta_slope / (delta_slope + psychrometric_constant * (1 + 0.34 * wind_speed_avg))
    weighting_aero = psychrometric_constant / (delta_slope + psychrometric_constant * (1 + 0.34 * wind_speed_avg))
    temperature_factor = 900 * wind_speed_avg / (T_mean + 273)

    # Saturation vapor pressure and actual vapor pressure
    e_saturation = (0.6108 * math.exp((17.27 * Tmax) / (Tmax + 237.3)) + 0.6108 * math.exp((17.27 * Tmin) / (Tmin + 237.3))) / 2
    e_actual = (0.6108 * math.exp((17.27 * Tmin) / (Tmin + 237.3)) * RH_max + 0.6108 * math.exp((17.27 * Tmax) / (Tmax + 237.3)) * RH_min) / 200

    # Extraterrestrial radiation and clear-sky radiation
    day_of_year = (current_date - pd.Timestamp(f'{year_selected}-01-01')).days + 1
    distance_factor = 1 + 0.033 * math.cos((2 * math.pi / 365) * day_of_year)
    solar_declination = 0.409 * math.sin((2 * math.pi / 365) * day_of_year - 1.39)

    latitude_rad = math.radians(latitude_deg)
    sunset_hour_angle = math.acos(-math.tan(latitude_rad) * math.tan(solar_declination))
    extraterrestrial_radiation = (24 * 60 / math.pi) * 0.0820 * distance_factor * (sunset_hour_angle * math.sin(latitude_rad) * math.sin(solar_declination) + math.cos(latitude_rad) * math.cos(solar_declination) * math.sin(sunset_hour_angle))
    clear_sky_radiation = (0.75 + 2e-5 * elevation_m) * extraterrestrial_radiation

    # Net shortwave and longwave radiation
    net_shortwave_radiation = (1 - 0.23) * solar_radiation_MJ
    net_longwave_radiation = 4.903e-9 * ((Tmax + 273.16) ** 4 + (Tmin + 273.16) ** 4) / 2 * (0.34 - 0.14 * math.sqrt(e_actual)) * (1.35 * (solar_radiation_MJ / clear_sky_radiation) - 0.35)

    # Net radiation
    net_radiation = net_shortwave_radiation - net_longwave_radiation
    net_radiation_MJ = 0.408 * net_radiation

    # Evapotranspiration calculation
    evapotranspiration = weighting_energy * net_radiation_MJ + weighting_aero * temperature_factor * (e_saturation - e_actual)
    evapotranspiration_values[i] = evapotranspiration

# Plot the evapotranspiration values over the days of the month
plt.figure(figsize=(10, 5))
plt.plot(day_indices, evapotranspiration_values, marker='o', linestyle='-', color='blue')

# Set plot labels and title
plt.xlabel('Day of Month')
plt.ylabel('Evapotranspiration (mm/day)')
plt.title(f'Evapotranspiration for {month_selected}/{year_selected}')
plt.grid(True)

# Display the plot
plt.show()

