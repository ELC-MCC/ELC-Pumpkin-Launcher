import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

# Load the data from the CSV file
file_path = 'C:/Users/Peter Cetner/Documents/pumpkin.csv'  # Adjust this path
df = pd.read_csv(file_path)

# Preparing the data
X = df[['mass(g)', 'pull strength(lbs)']].values  # Features: mass and pull strength
y = df['distance feet'].values  # Target variable: distance

# Adding a column of ones for the intercept term
X_b = np.c_[np.ones(X.shape[0]), X]  # Add bias term

# Calculating the coefficients using the normal equation
theta_best = np.linalg.inv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)

# Predicting the required pull strength to achieve a target distance
def calculate_force(mass, target_distance):
    pull_strength = (target_distance - theta_best[0] - theta_best[1] * mass) / theta_best[2]
    return pull_strength

# Function to create the plot
def create_plot(mass=None, target_distance=None):
    ax.clear()
    num_points = 5  # Decrease the number of points for a less dense mesh
    x_range = np.linspace(df['mass(g)'].min(), df['mass(g)'].max(), num_points)
    y_range = np.linspace(df['distance feet'].min(), df['distance feet'].max(), num_points)

    x_mesh, y_mesh = np.meshgrid(x_range, y_range)
    z_mesh = np.array([calculate_force(x, y) for x, y in zip(np.ravel(x_mesh), np.ravel(y_mesh))])
    z_mesh = z_mesh.reshape(x_mesh.shape)

    sns.set_style('darkgrid')
    sns.set_palette('husl')

    # Plot with updated colors for dark theme
    ax.scatter(df['mass(g)'], df['pull strength(lbs)'], df['distance feet'], color='lightblue', marker='o', s=100)
    ax.plot_wireframe(x_mesh, z_mesh, y_mesh, color='#2ECC71', alpha=0.8)

    if mass is not None and target_distance is not None:
        required_pull_strength = calculate_force(mass, target_distance)
        ax.scatter(mass, required_pull_strength, target_distance, color='#E74C3C', marker='o', s=200, label='Prediction')

    # Update plot styling for dark theme
    ax.set_facecolor('#1E272E')
    ax.xaxis.label.set_color('#D3E0EA')
    ax.yaxis.label.set_color('#D3E0EA')
    ax.zaxis.label.set_color('#D3E0EA')
    ax.tick_params(colors='#D3E0EA', labelsize=16)
    
    ax.set_xlabel('Mass (g)', fontsize=16)
    ax.set_ylabel('Pull Strength (lbs)', fontsize=16)
    ax.set_zlabel('Distance (feet)', fontsize=16)
    ax.set_title('3D Scatter Plot of Mass, Pull Strength, and Distance', fontsize=18, color='#D3E0EA')
    ax.legend(fontsize=18)
    
    canvas.draw()

# GUI setup
def on_predict(event=None):
    try:
        mass = float(mass_entry.get())
        target_distance = float(distance_entry.get())
        required_pull_strength = calculate_force(mass, target_distance)

        # Clear previous entries in the result_table
        for item in result_table.get_children():
            result_table.delete(item)

        # Insert the new results into the table
        result_table.insert('', 'end', values=("Force (lbs):", f"{required_pull_strength:.1f}"))
        result_table.insert('', 'end', values=("Mass (g):", mass))
        result_table.insert('', 'end', values=("Distance (feet):", target_distance))

        create_plot(mass, target_distance)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for mass and target distance.")

# Function to close the application
def on_exit(event=None):
    root.destroy()

# Creating main GUI window with theme
root = tk.Tk()
root.title("Force Prediction GUI")
root.geometry("1920x1080")
root.configure(bg='#1E272E')  # Dark background

# Configure the style
style = ttk.Style()
style.theme_use('clam')

# Configure styles for different widget types
style.configure('TFrame', background='#1E272E')
style.configure('TLabel',
    background='#1E272E',
    foreground='#D3E0EA',
    font=("Helvetica", 18))
style.configure('TEntry',
    fieldbackground='#2C3A47',
    foreground='#D3E0EA',
    font=("Helvetica", 48),
    padding=(10, 5))
style.configure('TButton',
    background='#27AE60',
    foreground='white',
    font=("Helvetica", 18),
    padding=(20, 10),
    borderwidth=0)
style.configure('Treeview',
    background='#2C3A47',
    fieldbackground='#2C3A47',
    foreground='#D3E0EA',
    font=("Helvetica", 48),
    rowheight=100)
style.configure('Treeview.Heading',
    background='#27AE60',
    foreground='white',
    font=("Helvetica", 18))

# Map styles for different widget states
style.map('TButton',
    background=[('active', '#2ECC71')],
    foreground=[('active', 'white')])
style.map('Treeview',
    background=[('selected', '#27AE60')],
    foreground=[('selected', 'white')])

# Key bindings
root.bind('<Return>', on_predict)
root.bind('<Escape>', on_exit)

# Create frames using ttk
input_frame = ttk.Frame(root)
input_frame.pack(side=tk.LEFT, padx=20, pady=20)

plot_frame = ttk.Frame(root)
plot_frame.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.BOTH, expand=True)

# Mass entry
ttk.Label(input_frame, text="Mass (g):").grid(row=0, column=0, padx=10, pady=10, sticky='e')
mass_entry = ttk.Entry(input_frame, font=("Segoe UI", 24))
mass_entry.grid(row=0, column=1, padx=10, pady=10)

# Target distance entry
ttk.Label(input_frame, text="Target Distance (f):").grid(row=1, column=0, padx=10, pady=10, sticky='e')
distance_entry = ttk.Entry(input_frame, font=("Segoe UI", 24))
distance_entry.grid(row=1, column=1, padx=10, pady=10)

# Predict button
predict_button = ttk.Button(input_frame, text="Predict", command=on_predict)
predict_button.grid(row=2, column=0, columnspan=2, padx=10, pady=20)

# Result table
result_table = ttk.Treeview(input_frame, columns=("Description", "Value"), show='headings', height=5)
result_table.heading("Description", text="", anchor='w')
result_table.heading("Value", text="", anchor='center')
result_table.column("Description", width=500, anchor='w')
result_table.column("Value", width=300, anchor='center')
result_table.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

# Create and configure the plot
fig = plt.Figure(figsize=(8, 5), dpi=100, facecolor='#1E272E')
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#1E272E')
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Initial plot
create_plot()

# Run the GUI
root.mainloop()