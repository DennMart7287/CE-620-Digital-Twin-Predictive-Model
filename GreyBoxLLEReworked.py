import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold

# 1. Load the multi-sheet Excel workbook
excel_path = r"C:\Users\ddzob\Downloads\CFD extractiedata Dennis TvH (3).xlsx"
xls = pd.ExcelFile(excel_path)
scenario_sheets = [s for s in xls.sheet_names if s != 'Blad1']

# 2. Extract comprehensive parameters per stage across all sheets
aggregated_rows = []
for sheet in scenario_sheets:
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
        sub_df = df.iloc[3:].copy()
        max_col = df.shape[1] - 1
        k_col = 30 if max_col >= 30 else (27 if max_col >= 27 else None)
        
        stages = pd.to_numeric(sub_df[10], errors='coerce')
        temps = pd.to_numeric(sub_df[11], errors='coerce')
        pressures = pd.to_numeric(sub_df[12], errors='coerce')
        flow_feed = pd.to_numeric(sub_df[14], errors='coerce')
        flow_solv = pd.to_numeric(sub_df[15], errors='coerce')
        
        w_feed_water = pd.to_numeric(sub_df[18], errors='coerce')
        w_feed_ether = pd.to_numeric(sub_df[19], errors='coerce')
        w_feed_solute = pd.to_numeric(sub_df[20], errors='coerce')
        
        w_extr_water = pd.to_numeric(sub_df[23], errors='coerce')
        w_extr_ether = pd.to_numeric(sub_df[24], errors='coerce')
        w_extr_solute = pd.to_numeric(sub_df[25], errors='coerce')
        
        if k_col is not None and k_col < df.shape[1]:
            k_solute = pd.to_numeric(sub_df[k_col], errors='coerce')
        else:
            k_solute = w_extr_solute / (w_feed_solute + 1e-9)

        stage_data = pd.DataFrame({
            'Stage': stages, 'Temperature': temps, 'Pressure': pressures,
            'Feed_Flow': flow_feed, 'Solvent_Flow': flow_solv,
            'Feed_Water': w_feed_water, 'Feed_Ether': w_feed_ether, 'Feed_Solute': w_feed_solute,
            'Extract_Water': w_extr_water, 'Extract_Ether': w_extr_ether, 'Extract_Solute': w_extr_solute,
            'K_Solute': k_solute
        }).dropna()
        
        aggregated_rows.append(stage_data)
    except Exception as e:
        continue

master_df = pd.concat(aggregated_rows, ignore_index=True)

# 3. Train multi-output estimators
features = ['Stage', 'Temperature', 'Feed_Flow', 'Solvent_Flow']
X = master_df[features].values
targets = ['Pressure', 'Feed_Water', 'Feed_Ether', 'Feed_Solute', 
           'Extract_Water', 'Extract_Ether', 'Extract_Solute', 'K_Solute']

models = {}
for target in targets:
    y = master_df[target].values
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    models[target] = model

print("\n--- Gray-Box LLE Model Successfully Trained on New Dataset ---")

# ==========================================
# 4. Interactive User Input & Thermodynamic Error-Handling
# ==========================================
print("\n" + "="*70)
print("INTERACTIVE LLE DIGITAL TWIN SIMULATOR")
print("="*70)

try:
    user_temp = float(input("Enter operating temperature (°C) [e.g., 20.1, 42, 110]: "))
    user_solvent = float(input("Enter solvent flow rate (kg/hr) [e.g., 201, 400]: "))
    user_feed = 130.0  # Standard baseline feed flow
    
    # --- Thermodynamic Guardrails / Error Handling ---
    solvent_boiling_point = 68.3  # Diisopropyl ether boiling point at 1 atm
    
    if user_temp >= solvent_boiling_point:
        raise ValueError(
            f"THERMODYNAMIC ERROR: Entered temperature ({user_temp}°C) exceeds or equals "
            f"the solvent boiling point ({solvent_boiling_point}°C at 1.013 bar). "
            f"The solvent (Di-Ether) will vaporize, forming a gas phase. Liquid-Liquid Extraction is impossible!"
        )
    if user_temp < 0:
        raise ValueError("THERMODYNAMIC ERROR: Temperature cannot be below 0°C (freezing point of aqueous feed).")
    if user_solvent <= 0:
        raise ValueError("THERMODYNAMIC ERROR: Solvent flow rate must be greater than 0 kg/hr.")

    print("\n[✔] Inputs validated successfully. Simulating extraction column stages...")

    # Run 10-stage simulation
    simulation_records = []
    for stage_idx in range(1, 11):
        sample_input = np.array([[stage_idx, user_temp, user_feed, user_solvent]])
        row_data = {'Stage': stage_idx, 'Temperature': user_temp, 'Solvent_Flow': user_solvent}
        for target in targets:
            row_data[target] = models[target].predict(sample_input)[0]
        simulation_records.append(row_data)

    sim_df = pd.DataFrame(simulation_records)
    
    # Print results summary table
    print("\n" + sim_df[['Stage', 'Feed_Solute', 'Extract_Solute', 'K_Solute']].to_string(index=False))
    
    # Export CSV and Plot Dashboard
    sim_df.to_csv("interactive_simulation_profile.csv", index=False)
    
    # Generate Dashboard Figure
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    axes[0, 0].plot(sim_df['Stage'], sim_df['Feed_Solute'], marker='o', color='crimson', label='Feed Solute')
    axes[0, 0].plot(sim_df['Stage'], sim_df['Extract_Solute'], marker='s', color='dodgerblue', label='Extract Solute')
    axes[0, 0].set_title(f"Solute Profile (T={user_temp}°C, Solv={user_solvent}kg/h)", fontweight='bold')
    axes[0, 0].set_ylabel("Mass Fraction")
    axes[0, 0].set_ylim([0, 1.0])
    axes[0, 0].legend()
    axes[0, 0].grid(True, linestyle=':', alpha=0.6)

    axes[0, 1].plot(sim_df['Stage'], sim_df['K_Solute'], marker='^', color='forestgreen', lw=2)
    axes[0, 1].set_title("Partition Coefficient ($K_D$)", fontweight='bold')
    axes[0, 1].set_ylabel("Distribution Ratio ($K$)")
    axes[0, 1].grid(True, linestyle=':', alpha=0.6)

    axes[1, 0].plot(sim_df['Stage'], sim_df['Feed_Water'], marker='o', color='teal', label='Feed Water')
    axes[1, 0].plot(sim_df['Stage'], sim_df['Extract_Water'], marker='s', color='orange', label='Extract Water')
    axes[1, 0].set_title("Water Mass Fractions", fontweight='bold')
    axes[1, 0].set_ylabel("Mass Fraction")
    axes[1, 0].set_ylim([0, 1.0])
    axes[1, 0].legend()
    axes[1, 0].grid(True, linestyle=':', alpha=0.6)

    axes[1, 1].plot(sim_df['Stage'], sim_df['Feed_Ether'], marker='o', color='purple', label='Feed Di-Ether')
    axes[1, 1].plot(sim_df['Stage'], sim_df['Extract_Ether'], marker='s', color='brown', label='Extract Di-Ether')
    axes[1, 1].set_title("Di-Ether Mass Fractions", fontweight='bold')
    axes[1, 1].set_ylabel("Mass Fraction")
    axes[1, 1].set_ylim([0, 1.0])
    axes[1, 1].legend()
    axes[1, 1].grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.savefig("interactive_simulation_plots.png", dpi=300)
    print("\n[✔] Simulation outputs saved ('interactive_simulation_profile.csv' & 'interactive_simulation_plots.png').")
    plt.show()

except ValueError as e:
    print(f"\n❌ SIMULATION REJECTED:\n{e}")