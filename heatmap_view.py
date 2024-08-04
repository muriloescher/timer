import tkinter as tk
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class HeatmapView:
    def __init__(self, root):
        # Create a frame for the heatmap view
        self.frame = tk.Frame(root)

        # Load and prepare data
        data = self.load_data("productivity_data.json")
        df = self.prepare_data_for_heatmap(data)

        # Plot the heatmap
        self.plot_heatmap(df)

    def load_data(self, file_path):
        """Load productivity data from JSON file."""
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            return {}

    def parse_date(self, date_str):
        """Parse date string into a datetime object."""
        return datetime.strptime(date_str, "%d.%m.%Y")

    def prepare_data_for_heatmap(self, data):
        """Prepare data for heatmap visualization."""
        focus_data = []
        for date_str, sessions in data.items():
            total_focus_duration = sum(session['focus_duration'] for session in sessions)
            focus_data.append((self.parse_date(date_str), total_focus_duration))

        # Create a DataFrame from the focus data
        df = pd.DataFrame(focus_data, columns=["date", "focus_duration"])
        df.set_index("date", inplace=True)

        # Resample to ensure all days of the past year are included
        start_date = datetime.now().date() - timedelta(days=365)
        end_date = datetime.now().date()
        df = df.reindex(pd.date_range(start_date, end_date, freq='D')).fillna(0)
        df['focus_duration'] = df['focus_duration'].astype(int)
        return df

    def plot_heatmap(self, df):
        """Plot the focus time heatmap."""
        # Prepare data for heatmap visualization
        df['week'] = df.index.to_series().apply(lambda x: x.strftime('%U'))
        df['weekday'] = df.index.weekday
        print(df)

        # Create a pivot table for the heatmap
        pd.set_option('display.max_columns', 60)
        pivot_table = df.pivot(index='weekday', columns='week', values='focus_duration')
        print(pivot_table.head(10))

        # Plot the heatmap
        fig, ax = plt.subplots(figsize=(14, 3))  # Adjust figsize to make it more rectangular like GitHub

        # 0 - 1, 1 - 3, 3 - 5, 5 - 7, 7+
        colors = ["#D3D3D3", "#25A244", "#1A7431", "#10451D"]
        # Define a colormap that shows low values as grey
        cmap = sns.color_palette(colors, as_cmap=True)

        # Calculate vmin and vmax based on the data
        vmin = pivot_table.values.min()
        vmax = pivot_table.values.max()

        # Ensure vmin < vmax
        if vmin == vmax:
            vmin = 0
            vmax = 1

        sns.heatmap(
            pivot_table,
            cmap=cmap,
            cbar=False,
            linewidths=0.5,
            linecolor='white',
            ax=ax,
            square=True,
            vmin=vmin,
            vmax=vmax
        )

        # Remove y-axis labels and ticks
        ax.set_yticks([])
        ax.set_ylabel('')

        # Set x-ticks for each month start
        start_date = df.index.min()
        month_labels = []
        month_positions = []

        for i, week in enumerate(pivot_table.columns):
            # Calculate week start date
            week_start_date = start_date + timedelta(weeks=int(week))
            if week_start_date.day <= 7:  # Rough approximation of month starts
                month_labels.append(week_start_date.strftime('%b'))
                month_positions.append(i)

        # Add spaces between months by creating 'empty' columns in pivot table
        for position in month_positions:
            ax.axvline(x=position - 0.5, color='white', linewidth=2)  # Slight line for visual separation

        ax.set_xticks(month_positions)
        ax.set_xticklabels(month_labels, rotation=45, ha='right')

        plt.title('Focus Time Heatmap (Past Year)')
        plt.xlabel('Month')
        plt.tight_layout()

        # Embed the plot into the Tkinter canvas
        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
