import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

# Load the data from the CSV file
file_path = 'C:/Users/morei/OneDrive/Connor The Maker/Pumpkin Launcher/pumpkin (1).csv'  # Adjust this path
df = pd.read_csv(file_path)

# Globals for model matrices
theta_best = None
X_b = None

# --- Refit helper (recomputes theta_best from current df) ---
def refit_from_df():
    global theta_best, X_b
    X = df[['mass(g)', 'pull strength(lbs)']].values  # Features: mass and pull strength
    y = df['distance feet'].values  # Target variable: distance
    X_b = np.c_[np.ones(X.shape[0]), X]  # Add bias term
    try:
        theta_best = np.linalg.inv(X_b.T @ X_b) @ (X_b.T @ y)
    except np.linalg.LinAlgError:
        # Fallback if matrix is singular (very few points or collinearity)
        theta_best = np.linalg.pinv(X_b) @ y

# Compute initial coefficients
refit_from_df()

# Predicting the required pull strength to achieve a target distance
def calculate_force(mass, target_distance):
    # theta_best: [b0, b_mass, b_pull]; solve for pull strength
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
    ax.scatter(df['mass(g)'], df['pull strength(lbs)'], df['distance feet'],
               color='lightblue', marker='o', s=100)
    ax.plot_wireframe(x_mesh, z_mesh, y_mesh, color='#2ECC71', alpha=0.8)

    added_label = False
    if mass is not None and target_distance is not None:
        required_pull_strength = calculate_force(mass, target_distance)
        ax.scatter(mass, required_pull_strength, target_distance,
                   color='#E74C3C', marker='o', s=200, label='Prediction')
        added_label = True

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
    if added_label:
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
        # Ensure this dialog stays above the main window
        messagebox.showerror(
            "Input Error",
            "Please enter valid numerical values for mass and target distance.",
            parent=root
        )

def on_exit(event=None):
    root.destroy()

# --- Data Collection window with live CSV view, add/edit/delete, fullscreen + always-on-top ---
def open_data_collection():
    win = tk.Toplevel(root)
    win.title("Data Collection")
    win.configure(bg='#1E272E')

    # Keep data window above main window & tied to it
    win.transient(root)
    win.lift()
    win.attributes('-topmost', True)

    # --- Fullscreen/Maximize on open ---
    try:
        win.state('zoomed')  # Windows: maximized (keeps taskbar)
    except tk.TclError:
        win.attributes('-fullscreen', True)  # Fallback
    win.geometry("900x700")  # Optional fallback size

    # ---- Top: entry form ----
    form = ttk.Frame(win)
    form.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(20, 10))

    ttk.Label(form, text="Mass (g):").grid(row=0, column=0, padx=8, pady=6, sticky='e')
    mass_e = ttk.Entry(form, font=("Segoe UI", 18), width=12)
    mass_e.grid(row=0, column=1, padx=8, pady=6)

    ttk.Label(form, text="Pull Strength (lbs):").grid(row=0, column=2, padx=8, pady=6, sticky='e')
    pull_e = ttk.Entry(form, font=("Segoe UI", 18), width=12)
    pull_e.grid(row=0, column=3, padx=8, pady=6)

    ttk.Label(form, text="Distance (feet):").grid(row=0, column=4, padx=8, pady=6, sticky='e')
    dist_e = ttk.Entry(form, font=("Segoe UI", 18), width=12)
    dist_e.grid(row=0, column=5, padx=8, pady=6)

    def clear_fields():
        mass_e.delete(0, 'end')
        pull_e.delete(0, 'end')
        dist_e.delete(0, 'end')
        mass_e.focus_set()

    # ---- Buttons ----
    btns = ttk.Frame(win)
    btns.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(0, 10))
    ttk.Button(btns, text="Add Row", command=lambda: add_row()).pack(side=tk.LEFT, padx=5)
    ttk.Button(btns, text="Update Selected", command=lambda: update_selected()).pack(side=tk.LEFT, padx=5)
    ttk.Button(btns, text="Delete Selected", command=lambda: delete_selected()).pack(side=tk.LEFT, padx=5)
    ttk.Button(btns, text="Clear Fields", command=clear_fields).pack(side=tk.LEFT, padx=5)
    ttk.Button(btns, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=5)

    # ---- Table container (with scrollbars) ----
    table_frame = ttk.Frame(win)
    table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    cols = list(df.columns)
    vscroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
    hscroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

    data_tree = ttk.Treeview(
        table_frame,
        columns=cols,
        show='headings',
        style='Tiny.Treeview',
        yscrollcommand=vscroll.set,
        xscrollcommand=hscroll.set,
        selectmode='extended'
    )
    vscroll.config(command=data_tree.yview)
    hscroll.config(command=data_tree.xview)

    vscroll.pack(side=tk.RIGHT, fill=tk.Y)
    hscroll.pack(side=tk.BOTTOM, fill=tk.X)
    data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for c in cols:
        data_tree.heading(c, text=c, anchor='w')
        data_tree.column(c, anchor='w', width=160)

    def refresh_table():
        # Reassert topmost in case a dialog changed stacking
        win.after(10, lambda: (win.lift(), win.attributes('-topmost', True)))
        data_tree.delete(*data_tree.get_children())
        for idx, row in df.iterrows():
            data_tree.insert('', 'end', iid=str(idx), values=tuple(row[c] for c in cols))

    def add_row():
        try:
            m = float(mass_e.get()); p = float(pull_e.get()); d = float(dist_e.get())
            global df
            new_row = pd.DataFrame({'mass(g)': [m], 'pull strength(lbs)': [p], 'distance feet': [d]})
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(file_path, index=False)
            refit_from_df(); create_plot(); refresh_table()
            messagebox.showinfo("Saved", "Row added, model updated.", parent=win)
            clear_fields()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter numeric values for all fields.", parent=win)

    def update_selected():
        sel = data_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a single row to update.", parent=win); return
        if len(sel) > 1:
            messagebox.showwarning("Multiple Selected", "Please select only one row to update.", parent=win); return
        try:
            m = float(mass_e.get()); p = float(pull_e.get()); d = float(dist_e.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter numeric values for all fields.", parent=win); return

        idx = int(sel[0])
        try:
            df.at[idx, 'mass(g)'] = m
            df.at[idx, 'pull strength(lbs)'] = p
            df.at[idx, 'distance feet'] = d
        except KeyError:
            messagebox.showerror("Update Error", "Could not update the selected row.", parent=win); return

        df.to_csv(file_path, index=False)
        refit_from_df(); create_plot(); refresh_table()
        try: data_tree.selection_set(str(idx))
        except tk.TclError: pass
        messagebox.showinfo("Updated", "Row updated and model refreshed.", parent=win)

    def delete_selected():
        sel = data_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select at least one row to delete.", parent=win); return

        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete {len(sel)} selected row(s)?",
                                   parent=win):
            return

        global df
        drop_idxs = [int(iid) for iid in sel]
        df = df.drop(index=drop_idxs).reset_index(drop=True)
        df.to_csv(file_path, index=False)
        refit_from_df(); create_plot(); refresh_table()
        messagebox.showinfo("Deleted", "Selected row(s) deleted and model refreshed.", parent=win)
        clear_fields()

    def on_row_select(event):
        sel = data_tree.selection()
        if not sel: return
        iid = sel[0]
        vals = data_tree.item(iid, 'values')
        if len(vals) == 3:
            clear_fields()
            mass_e.insert(0, vals[cols.index('mass(g)')])
            pull_e.insert(0, vals[cols.index('pull strength(lbs)')])
            dist_e.insert(0, vals[cols.index('distance feet')])

    data_tree.bind('<<TreeviewSelect>>', on_row_select)

    # Reassert topmost periodically (paranoid fix for some window managers)
    win.after(50, lambda: (win.lift(), win.attributes('-topmost', True)))

    # Keyboard shortcuts
    win.bind('<Return>', lambda e: add_row())
    win.bind('<Escape>', lambda e: win.destroy())

    refresh_table()
    mass_e.focus_set()

# Creating main GUI window with theme
root = tk.Tk()
root.title("Force Prediction GUI")
root.configure(bg='#1E272E')

# --- Fullscreen/Maximize on open ---
try:
    root.state('zoomed')  # Windows: maximized (keeps taskbar)
except tk.TclError:
    root.attributes('-fullscreen', True)  # Fallback
root.geometry("1920x1080")  # Optional fallback size

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

# --- Smaller table style for the data window ---
style.configure('Tiny.Treeview',
    background='#2C3A47',
    fieldbackground='#2C3A47',
    foreground='#D3E0EA',
    font=("Helvetica", 16),
    rowheight=28)
style.configure('Tiny.Treeview.Heading',
    background='#27AE60',
    foreground='white',
    font=("Helvetica", 14))

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
root.bind('<Control-d>', lambda e: open_data_collection())  # Optional shortcut

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
ttk.Label(input_frame, text="Target Distance (ft):").grid(row=1, column=0, padx=10, pady=10, sticky='e')
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

# Button to open the Data Collection window
ttk.Button(input_frame, text="Open Data Collection", command=open_data_collection)\
    .grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

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