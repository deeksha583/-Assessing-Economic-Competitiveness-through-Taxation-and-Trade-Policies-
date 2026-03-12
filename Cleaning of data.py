import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

def fill_missing_values(df, countries):
    """Fill missing values (..) using interpolation and trend analysis"""
    
    # Replace ".." with NaN for numeric operations
    for country in countries:
        df[country] = pd.to_numeric(df[country], errors='coerce')
    
    # Fill missing values using interpolation
    for country in countries:
        series = df[country].copy()
        
        # Linear interpolation for internal missing values
        df[country] = series.interpolate(method='linear', limit_direction='both')
        
        # For remaining NaN (edge cases), use polynomial fit
        mask = df[country].isna()
        if mask.any():
            valid_idx = ~mask
            if valid_idx.sum() > 2:
                x = np.array(df.loc[valid_idx, 'Year'])
                y = np.array(df.loc[valid_idx, country])
                
                # Fit polynomial (degree 2)
                z = np.polyfit(x, y, 2)
                p = np.poly1d(z)
                
                # Fill NaN values using polynomial
                for idx in df[df[country].isna()].index:
                    year_val = df.loc[idx, 'Year']
                    df.loc[idx, country] = p(year_val)
    
    # Round to 2 decimal places
    for country in countries:
        df[country] = df[country].round(2)
    
    return df

def create_table_and_chart(csv_file, title, table_output, chart_output):
    """Create a formatted table and chart from CSV file with filled missing values"""
    print(f"\nProcessing: {csv_file}")
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Filter for the three countries
    countries = ['India', 'China', 'United States']
    df_filtered = df[df['Country Name'].isin(countries)].copy()
    
    # Extract year columns (2000-2023)
    year_columns = [f'{year} [YR{year}]' for year in range(2000, 2024)]
    
    # Create a new dataframe with Year as index
    data = {'Year': list(range(2000, 2024))}
    
    # Get data for each country
    for country in countries:
        country_data = df_filtered[df_filtered['Country Name'] == country]
        if len(country_data) > 0:
            data[country] = []
            for year_col in year_columns:
                value = country_data[year_col].values[0]
                # Convert to float or keep as NaN marker
                if value == '..':
                    data[country].append(np.nan)
                else:
                    try:
                        data[country].append(float(value))
                    except:
                        data[country].append(np.nan)
    
    # Create dataframe for the table
    table_df = pd.DataFrame(data)
    
    # Fill missing values
    table_df = fill_missing_values(table_df, countries)
    
    # Display the table
    print(f"\n{title}\n")
    print(table_df.to_string(index=False))
    
    # Save table to CSV
    table_df.to_csv(table_output, index=False)
    print(f"Table saved as '{table_output}'")
    
    # Create chart
    plt.figure(figsize=(12, 6))
    
    for country in countries:
        plt.plot(table_df['Year'], table_df[country], marker='o', linewidth=2, label=country, markersize=4)
    
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Value', fontsize=12, fontweight='bold')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.legend(fontsize=11, loc='best')
    plt.grid(True, alpha=0.3)
    plt.xticks(range(2000, 2024, 2), rotation=45)
    plt.tight_layout()
    
    # Save chart
    plt.savefig(chart_output, dpi=300, bbox_inches='tight')
    print(f"Chart saved as '{chart_output}'\n")
    plt.close()

# Current directory
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")

# Create tables and charts for all three datasets
create_table_and_chart('Total Tax Revenue.csv', 
                      '📊 Table 1 – Tax Revenue (% of GDP)', 
                      'Tax Revenue Table.csv',
                      'Tax Revenue Chart.png')

create_table_and_chart('Tariff Rate.csv', 
                      '📊 Table 2 – Tariff Rate', 
                      'Tariff Rate Table.csv',
                      'Tariff Rate Chart.png')

create_table_and_chart('Trade Openness.csv', 
                      '📊 Table 3 – Trade Openness', 
                      'Trade Openness Table.csv',
                      'Trade Openness Chart.png')

print("="*60)
print("All tables and charts have been generated successfully!")
print("="*60)
print("\nGenerated files:")
print("✓ Tax Revenue Table.csv + Tax Revenue Chart.png")
print("✓ Tariff Rate Table.csv + Tariff Rate Chart.png")
print("✓ Trade Openness Table.csv + Trade Openness Chart.png")

