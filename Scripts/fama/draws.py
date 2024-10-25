import pandas as pd
import matplotlib.pyplot as plt


# Function to read CSV and plot the data
def plot_from_csv(file, ax):
    csv_file = f"{file}.csv"
    df = pd.read_csv(csv_file)
    ax.plot(df['Year'], df['Winners'], marker='o', label='Winners', color='green')
    ax.plot(df['Year'], df['Median'], marker='o', label='Median', color='black')
    ax.plot(df['Year'], df['Losers'], marker='o', label='Losers', color='red')
    ax.plot(df['Year'], df['DJI'], marker='o', label='DJI', color='blue')
    ax.plot(df['Year'], df['EW'], marker='o', label='EW', color='orange')
    ax.set_title(f'{file}')
    ax.set_xlabel('Year')
    ax.set_ylim([-15, 15])
    ax.set_ylabel('Coefficient Value')
    ax.legend()
    ax.grid(True)


# Create a figure with 3 subplots
fig, axs = plt.subplots(3, 1, figsize=(15, 20))

# List of CSV files to plot
csv_files = ['a1', 'a2', 'a3']

# Plot each CSV file in a separate subplot
for i, csv_file in enumerate(csv_files):
    plot_from_csv(csv_file, axs[i])

# Adjust layout and save the figure
plt.tight_layout()
plt.savefig('combined_performance_plot.png')
