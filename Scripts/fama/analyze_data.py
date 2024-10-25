import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt


def fit_regression_per_year_no_intercept(df, strategy_column):
    """
    Fits a regression line for each year using the given strategy returns and Fama-French factors, without an intercept.

    Parameters:
    df (pd.DataFrame): DataFrame containing the returns and Fama-French factors
    strategy_column (str): The column name of the strategy to be analyzed

    Returns:
    pd.DataFrame: DataFrame containing the coefficients (a1, a2, a3) for each year
    """
    coefficients = []
    years = df['Year'].unique()

    for year in years:
        yearly_data = df[df['Year'] == year]
        X = yearly_data[['Mkt-RF', 'SMB', 'HML']]
        Y = yearly_data[strategy_column]

        if len(Y) > 0:  # Ensure there are enough data points for regression
            model = sm.OLS(Y, X).fit()
            params = model.params
            coefficients.append({
                'Year': year,
                'Mkt-RF': params['Mkt-RF'],
                'SMB': params['SMB'],
                'HML': params['HML']
            })
        else:
            coefficients.append({
                'Year': year,
                'Mkt-RF': None,
                'SMB': None,
                'HML': None
            })

    return pd.DataFrame(coefficients)


def plot_coefficients(coefficients_df, strategy_name):
    """
    Plots the coefficients for each year with bars and colors for each factor.

    Parameters:
    coefficients_df (pd.DataFrame): DataFrame containing the coefficients
    strategy_name (str): The name of the strategy for the plot title
    """
    coefficients_df.set_index('Year', inplace=True)
    coefficients_df.plot(kind='bar', figsize=(15, 7))
    plt.title(f"Regression Coefficients for {strategy_name}")
    plt.xlabel("Year")
    plt.ylabel("Coefficient Value")
    plt.legend(title="Factors")
    plt.show()


def calculate_percentage_contributions(merged_df, coefficients_df):
    """
    Calculates the percentage contribution of each factor (Mkt-RF, SMB, HML) by dividing the contribution by the total contribution.

    Parameters:
    merged_df (pd.DataFrame): DataFrame containing the returns and Fama-French factors
    coefficients_df (pd.DataFrame): DataFrame containing the coefficients

    Returns:
    pd.DataFrame: DataFrame containing the percentage factor contributions for each year
    """
    merged_df = pd.merge(merged_df, coefficients_df, on='Year')

    # Calculate the contribution of each factor
    merged_df['Mkt-RF Contribution'] = merged_df['Mkt-RF_x'] * merged_df['Mkt-RF_y']
    merged_df['SMB Contribution'] = merged_df['SMB_x'] * merged_df['SMB_y']
    merged_df['HML Contribution'] = merged_df['HML_x'] * merged_df['HML_y']

    # Calculate total contribution
    merged_df['Total Contribution'] = (merged_df['Mkt-RF Contribution'] +
                                       merged_df['SMB Contribution'] +
                                       merged_df['HML Contribution'])

    # Calculate the percentage contribution of each factor
    merged_df['Mkt-RF %'] = (merged_df['Mkt-RF Contribution'] / merged_df['Total Contribution']) * 100
    merged_df['SMB %'] = (merged_df['SMB Contribution'] / merged_df['Total Contribution']) * 100
    merged_df['HML %'] = (merged_df['HML Contribution'] / merged_df['Total Contribution']) * 100

    # Select only the percentage columns to return
    percentage_contributions_df = merged_df[['Year', 'Mkt-RF %', 'SMB %', 'HML %']]
    return percentage_contributions_df


def plot_percentage_contributions(percentage_contributions_df, strategy_name):
    """
    Plots the percentage contributions for each year.

    Parameters:
    percentage_contributions_df (pd.DataFrame): DataFrame containing the percentage contributions
    strategy_name (str): The name of the strategy for the plot title
    """
    percentage_contributions_df.set_index('Year', inplace=True)
    percentage_contributions_df.plot(kind='bar', stacked=True, figsize=(15, 7))
    plt.title(f"Percentage Factor Contributions to {strategy_name} Return")
    plt.xlabel("Year")
    plt.ylabel("Percentage Contribution")
    plt.legend(title="Factors")
    plt.show()


# Manually entering the strategy returns data based on the provided image
strategy_returns = {
    'Year': [1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016,
             2017, 2018, 2019, 2020, 2021, 2022, 2023],
    'Winners': [34.7, -22.2, -12.1, -19.4, 24, 29.9, 26, 5.9, 17, -30.3, 14.4, 12.8, 14.8, 12.1, 36.5, 15.6, 11, 7.6,
                25.9, 2.2, 24.9, 21.3, 23.7, -7.9, 5],
    'Losers': [34.7, 13.3, 5.9, -14.7, 51.3, 6.6, 3.6, 18.2, 6.4, -33.2, 59, 13.1, -1.1, 25.8, 30.1, 9.2, -1, 21.8,
               24.7, -2.6, 23.3, -2.5, 20.5, -7.4, 26.8],
    'EW': [34, 5.7, -3.6, -14.6, 35.4, 17.9, 11.3, 15.6, 15.5, -29.5, 37.6, 15.8, 7.6, 17.5, 34.6, 16.1, 3.3, 14.2,
           28.2, 0, 26.4, 8.4, 19.2, -6.1, 17.2],
    'DJI': [25.2, -6.2, -7.1, -16.8, 25.3, 3.1, -0.6, 16.3, 6.4, -33.8, 18.8, 11, 5.5, 7.3, 26.5, 7.5, -2.2, 13.4, 25.1,
            -5.6, 22.3, 7.2, 18.7, -8.8, 13.7],
    'Median': [38.8, 26.5, -7.3, -14.4, 33.5, 16.3, 1.6, 20.2, 21.3, -26.5, 45.7, 24.6, 11.1, 13.5, 39, 23.1, -0.9,
               12.5, 32.7, -1.9, 32.2, 7.2, 12.6, -3.3, 18.3]
}

# Load the Fama-French factor data
fama_french_data = pd.read_csv('updated_ff.csv')

# Prepare the data by aligning the years and calculating the annual factors
fama_french_data['Year'] = pd.to_datetime(fama_french_data['Date'], format='%Y%m').dt.year
fama_french_annual = fama_french_data.groupby('Year').mean().reset_index()

strategies_data = pd.DataFrame(strategy_returns)
merged_data = pd.merge(strategies_data, fama_french_annual, on='Year')

# Get coefficients for each strategy and plot
for strat in ["Winners", "Losers", "EW", "DJI", "Median"]:
    coefficients_df = fit_regression_per_year_no_intercept(merged_data, strat)
    print(coefficients_df)

    # Calculate percentage factor contributions
    percentage_contributions_df = calculate_percentage_contributions(merged_data, coefficients_df)

    # Plot the percentage factor contributions
    plot_percentage_contributions(percentage_contributions_df, strat)

    # Uncomment the below line to save coefficients to CSV
    coefficients_df.to_csv(f"{strat}_coef_.csv", index=False)


## % contribution to returns by 3 Fama-French factors.