# ELC Pumpkin Launcher - Linear Regression Model

This repository contains a Python application developed for the Engineering Learning Community (ELC) Pumpkin Launcher project. It uses a Linear Regression model to predict the required pull strength for a pumpkin launcher to hit a specific target distance based on the pumpkin's mass.

## Features

- **Force Prediction**: Calculates the necessary pull strength (lbs) given a target distance (ft) and pumpkin mass (g).
- **3D Visualization**: visualizes the relationship between Mass, Pull Strength, and Distance using an interactive 3D scatter and wireframe plot.
- **Data Collection**: A built-in GUI to add, update, and delete experimental data points, which automatically updates the regression model.
- **Dark Mode GUI**: A sleek, dark-themed user interface built with Tkinter.

## Prerequisites

- Python 3.x
- `tkinter` (usually included with Python)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/ELC-MCC/ELC-Pumpkin-Launcher.git
    cd ELC-Pumpkin-Launcher
    ```

2.  **Install dependencies**:
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application**:
    ```bash
    python p-LR-model.py
    ```

2.  **Using the Predictive Tool**:
    - Enter the **Mass** of the pumpkin in grams.
    - Enter the **Target Distance** in feet.
    - Click **Predict** to see the calculate Force (lbs) and visualize the point on the 3D plot.

3.  **Managing Data**:
    - Click **Open Data Collection** to view the underlying dataset.
    - **Add Row**: Enter Mass, Pull Strength, and Distance, then click "Add Row".
    - **Update/Delete**: Select a row from the table to update or delete it.
    - The model retrains automatically when data is modified.

## Configuration

> [!IMPORTANT]
> **File Paths**: The script currently uses a hardcoded file path for the CSV data file.
> 
> Open `p-LR-model.py` and look for the line:
> ```python
> file_path = 'C:/Users/morei/OneDrive/Connor The Maker/Pumpkin Launcher/pumpkin (1).csv'
> ```
> Update this path to point to the location of your `pumpkin.csv` file on your local machine.

## Files

- `p-LR-model.py`: The main application script including the GUI, model logic, and visualization.
- `pumpkinPERCENTerror.py`: An alternative script focused on error analysis and plotting.
- `pumpkin 2024.csv` / `pumpkin 2025.csv`: Historical data files.
