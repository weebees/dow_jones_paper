import os
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt


# Function to load Fama-French data and strategy returns
def load_data(fama_french_file, strategy_returns):
    # Load Fama-French data
    fama_french_data = pd.read_csv(fama_french_file)

    # Extract years from Fama-French data
    fama_french_data['Year'] = fama_french_data['Date'].astype(str).str[:4].astype(int)

    # Average annual factors
    annual_factors = fama_french_data.groupby('Year').mean().reset_index()

    # Convert strategy returns dictionary to DataFrame
    strategy_df = pd.DataFrame(strategy_returns)

    # Merge strategy returns with Fama-French factors
    merged_data = pd.merge(strategy_df, annual_factors, on='Year')

    return merged_data


# Function to fit the Fama-French 3-factor model
def fama_french_fit(returns, fama_factors):
    # Prepare independent variables (Market, SMB, HML)
    X = fama_factors[['Mkt-RF', 'SMB', 'HML']]
    X = sm.add_constant(X)  # Add constant for excess return
    # Dependent variable: strategy excess return
    y = returns - fama_factors['RF']
    # Fit the model
    model = sm.OLS(y, X).fit()
    return model.params


def plot_factor_contributions(years, strategy, constant, market_contrib, smb_contrib, hml_contrib, output_directory,
                              percentage=False):
    plt.figure(figsize=(10, 6))

    if percentage:
        # Normalize the contributions to show percentages
        total_contributions = constant + market_contrib + smb_contrib + hml_contrib
        constant_perc = constant / total_contributions
        hml_perc = hml_contrib / total_contributions
        smb_perc = smb_contrib / total_contributions
        market_perc = market_contrib / total_contributions

        # Plot as percentages in the correct order: Constant, HML, SMB, Market (Mkt-RF)
        plt.bar(years, constant_perc, label='Constant (Excess Return)', color='yellow')
        plt.bar(years, hml_perc, label='HML', bottom=constant_perc, color='red')
        plt.bar(years, smb_perc, label='SMB', bottom=constant_perc + hml_perc, color='green')
        plt.bar(years, market_perc, label='Market (Mkt-RF)', bottom=constant_perc + hml_perc + smb_perc, color='blue')

        plt.title(f'Fama-French Factor Contributions as Percentage for {strategy}')
        plt.ylabel('Percentage Contribution')
    else:
        # Plot the absolute contributions in the correct order: Constant, HML, SMB, Market (Mkt-RF)
        plt.bar(years, constant, label='Constant (Excess Return)', color='yellow')
        plt.bar(years, hml_contrib, label='HML', bottom=constant, color='red')
        plt.bar(years, smb_contrib, label='SMB', bottom=constant + hml_contrib, color='green')
        plt.bar(years, market_contrib, label='Market (Mkt-RF)', bottom=constant + hml_contrib + smb_contrib,
                color='blue')

        plt.title(f'Fama-French Factor Contributions for {strategy}')
        plt.ylabel('Return Contribution')

    plt.xlabel('Year')
    plt.legend()
    plt.tight_layout()

    # Save the plot as a PNG file
    if percentage:
        plt.savefig(os.path.join(output_directory, f"{strategy}_fama_french_contributions_percentage.png"))
    else:
        plt.savefig(os.path.join(output_directory, f"{strategy}_fama_french_contributions.png"))

    plt.close()


# Function to save coefficients dataframe to CSV
def save_coefficients(coefficients_df, output_directory):
    coefficients_df.to_csv(os.path.join(output_directory, "fama_french_coefficients.csv"), index=True)


def calculate_percentage_contributions(years, coefficients_df, merged_data, strategies):
    percentage_contributions = []

    for strategy in strategies:
        constant = coefficients_df.loc[strategy, 'Constant']
        market_contrib = coefficients_df.loc[strategy, 'Mkt-RF'] * merged_data['Mkt-RF']
        smb_contrib = coefficients_df.loc[strategy, 'SMB'] * merged_data['SMB']
        hml_contrib = coefficients_df.loc[strategy, 'HML'] * merged_data['HML']

        # Calculate total contributions per year
        total_contrib = constant + market_contrib + smb_contrib + hml_contrib

        # Calculate percentage contributions
        constant_perc = constant / total_contrib
        market_perc = market_contrib / total_contrib
        smb_perc = smb_contrib / total_contrib
        hml_perc = hml_contrib / total_contrib

        # Create a DataFrame row for each year with percentage contributions
        for i, year in enumerate(years):
            percentage_contributions.append({
                'Year': year,
                'Strategy': strategy,
                'Constant (%)': constant_perc[i],
                'Market (Mkt-RF) (%)': market_perc[i],
                'SMB (%)': smb_perc[i],
                'HML (%)': hml_perc[i]
            })

    # Convert the list to a DataFrame
    percentage_contributions_df = pd.DataFrame(percentage_contributions)

    return percentage_contributions_df


def save_percentage_contributions_to_csv(percentage_contributions_df, output_directory):
    output_file = os.path.join(output_directory, 'annual_percentage_contributions.csv')
    percentage_contributions_df.to_csv(output_file, index=False)


def main(fama_french_file, strategy_returns, output_directory):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Load data
    merged_data = load_data(fama_french_file, strategy_returns)

    # Fit the model for each strategy
    strategies = ['Winners', 'Losers', 'Median']
    coefficients = {}
    for strategy in strategies:
        coeff = fama_french_fit(merged_data[strategy], merged_data)
        coefficients[strategy] = coeff

    # Convert coefficients dictionary to DataFrame for better display and save to CSV
    coefficients_df = pd.DataFrame(coefficients).T
    coefficients_df.columns = ['Constant', 'Mkt-RF', 'SMB', 'HML']
    save_coefficients(coefficients_df, output_directory)

    # Calculate and save annual percentage contributions
    years = merged_data['Year']
    percentage_contributions_df = calculate_percentage_contributions(years, coefficients_df, merged_data, strategies)
    save_percentage_contributions_to_csv(percentage_contributions_df, output_directory)

    # Plot results for each strategy and save the plots
    for strategy in strategies:
        constant = coefficients_df.loc[strategy, 'Constant']
        market_contrib = coefficients_df.loc[strategy, 'Mkt-RF'] * merged_data['Mkt-RF']
        smb_contrib = coefficients_df.loc[strategy, 'SMB'] * merged_data['SMB']
        hml_contrib = coefficients_df.loc[strategy, 'HML'] * merged_data['HML']

        # Plot absolute contributions
        plot_factor_contributions(years, strategy, constant, market_contrib, smb_contrib, hml_contrib, output_directory)
        # Plot percentage contributions
        plot_factor_contributions(years, strategy, constant, market_contrib, smb_contrib, hml_contrib, output_directory,
                                  percentage=True)


# Example strategy returns data
strategy_returns = {
    'Year': [1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016,
             2017, 2018, 2019, 2020, 2021, 2022, 2023],
    'Winners': [34.7, -22.2, -12.1, -19.4, 24, 29.9, 26, 5.9, 17, -30.3, 14.4, 12.8, 14.8, 12.1, 36.5, 15.6, 11, 7.6,
                25.9, 2.2, 24.9, 21.3, 23.7, -7.9, 5],
    'Losers': [34.7, 13.3, 5.9, -14.7, 51.3, 6.6, 3.6, 18.2, 6.4, -33.2, 59, 13.1, -1.1, 25.8, 30.1, 9.2, -1, 21.8,
               24.7, -2.6, 23.3, -2.5, 20.5, -7.4, 26.8],
    'Median': [38.8, 26.5, -7.3, -14.4, 33.5, 16.3, 1.6, 20.2, 21.3, -26.5, 45.7, 24.6, 11.1, 13.5, 39, 23.1, -0.9,
               12.5, 32.7, -1.9, 32.2, 7.2, 12.6, -3.3, 18.3]
}

# File path to Fama-French data
fama_french_file = 'updated_ff1.csv'

# Define output directory
output_directory = 'output_directory'

# Run the main function
main(fama_french_file, strategy_returns, output_directory)
