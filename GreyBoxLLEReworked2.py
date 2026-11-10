import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

# 1. Load the multi-sheet Excel workbook
excel_path = r"C:\Users\ddzob\Downloads\CFD extractiedata Dennis TvH (3).xlsx"
xls = pd.ExcelFile(excel_path)
scenario_sheets = [s for s in xls.sheet_names if s != 'Blad1']

# 2. Extract comprehensive parameters per sheet
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

# Print dataset bounds to guide user input
print(f"\n[INFO] Aspen Dataset Loaded Successfully.")
print(f"       -> Temperature Range in Training Data: {master_df['Temperature'].min():.1f}°C to {master_df['Temperature'].max():.1f}°C")
print(f"       -> Solvent Flow Range in Training Data: {master_df['Solvent_Flow'].min():.1f} to {master_df['Solvent_Flow'].max():.1f} kg/hr")
print(f"       -> Feed Flow Range in Training Data: {master_df['Feed_Flow'].min():.1f} to {master_df['Feed_Flow'].max():.1f} kg/hr")

# 3. Train multi-output estimators
features = ['Stage', 'Temperature', 'Feed_Flow', 'Solvent_Flow']
X = master_df[features].values
targets = ['Pressure', 'Feed_Water', 'Feed_Ether', 'Feed_Solute', 
           'Extract_Water', 'Extract_Ether', 'Extract_Solute', 'K_Solute']

models = {}
for target in targets:
    y = master_df[target].values
    # model = RandomForestRegressor(n_estimators=100, random_state=42)
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    models[target] = model

print("\n--- Full Aspen-Range Digital Model Successfully Trained ---")

# ==========================================
# 4. Interactive Simulator (Aspen Dataset Bounds)
# ==========================================
print("\n" + "="*70)
print("ASPEN-BASED EXTRACTION COLUMN - DIGITAL MODEL SIMULATOR")
print("="*70)

try:
    user_temp = float(input("Enter operating temperature (°C) [Aspen Range: ~4.2 - 104.2°C]: "))
    user_solvent = float(input("Enter solvent flow rate (kg/hr) [Aspen Range: ~88 - 448 kg/hr]: "))
    user_feed = float(input("Enter feed flow rate (kg/hr) [Aspen Range: ~80 - 140 kg/hr]: "))
    
    # --- Thermodynamic Guardrails ---
    SOLVENT_BOILING_POINT = 68.3  # Diisopropyl ether boiling point at 1.013 bar[cite: 3]
    
    if user_temp >= SOLVENT_BOILING_POINT:
        raise ValueError(
            f"THERMODYNAMIC ERROR: Temperature ({user_temp}°C) exceeds solvent "
            f"boiling point ({SOLVENT_BOILING_POINT}°C). Di-Ether vaporizes; liquid-liquid extraction fails!"
        )
    if user_temp < 0:
        raise ValueError("ERROR: Temperature cannot be below 0°C.")
    if user_solvent <= 0 or user_feed <= 0:
        raise ValueError("ERROR: Flow rates must be strictly greater than 0.")

    print("\n[✔] Thermodynamic checks passed. Simulating column stages across Aspen dataset space...")

    # Run 10-stage simulation
    simulation_records = []
    for stage_idx in range(1, 11):
        sample_input = np.array([[stage_idx, user_temp, user_feed, user_solvent]])
        row_data = {'Stage': stage_idx, 'Temperature': user_temp, 'Feed_Flow': user_feed, 'Solvent_Flow': user_solvent}
        for target in targets:
            row_data[target] = models[target].predict(sample_input)[0]
        simulation_records.append(row_data)

    sim_df = pd.DataFrame(simulation_records)
    print("\n" + sim_df[['Stage', 'Feed_Solute', 'Extract_Solute', 'K_Solute']].to_string(index=False))
    sim_df.to_csv("aspen_range_simulation_output.csv", index=False)
    
    # ==========================================
    # 5. Enhanced 5-Panel Dashboard with Training Scatter Overlay
    # ==========================================
    fig, axes = plt.subplots(3, 2, figsize=(14, 15))
    
    # Panel 1: Solute Concentration Profile across Stages
    axes[0, 0].plot(sim_df['Stage'], sim_df['Feed_Solute'], marker='o', color='crimson', label='Feed Solute (Aqueous)')
    axes[0, 0].plot(sim_df['Stage'], sim_df['Extract_Solute'], marker='s', color='dodgerblue', label='Extract Solute (Organic)')
    axes[0, 0].set_title(f"Solute Concentration Profile (T={user_temp}°C, Solv={user_solvent}kg/h)", fontweight='bold')
    axes[0, 0].set_ylabel("Mass Fraction")
    axes[0, 0].set_ylim([0, 1.0])
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(True, linestyle=':', alpha=0.6)

    # Panel 2: Partition Coefficient Profile (K_D)
    axes[0, 1].plot(sim_df['Stage'], sim_df['K_Solute'], marker='^', color='forestgreen', lw=2)
    axes[0, 1].set_title("Partition Coefficient Profile ($K_D$)", fontweight='bold')
    axes[0, 1].set_ylabel("Distribution Ratio ($K$)")
    axes[0, 1].grid(True, linestyle=':', alpha=0.6)

    # Panel 3: Phase Equilibrium Distribution Curve (Y vs X) with Training Scatter Background
    train_x = master_df['Feed_Solute'].values
    train_y = master_df['Extract_Solute'].values
    
    axes[1, 0].scatter(train_x, train_y, color='lightgray', s=15, alpha=0.6, label='Historical Training Scenarios (Aspen)')
    
    x_sim = sim_df['Feed_Solute'].values
    y_sim = sim_df['Extract_Solute'].values
    axes[1, 0].plot(x_sim, y_sim, marker='D', color='darkviolet', lw=2, label='Current Simulation Path')
    
    max_limit = max(max(train_x), max(train_y)) * 1.1
    axes[1, 0].plot([0, max_limit], [0, max_limit], color='gray', linestyle='--', label='45° Reference ($Y=X$)')
    
    axes[1, 0].set_title("Phase Equilibrium Distribution Curve ($Y$ vs $X$)", fontweight='bold')
    axes[1, 0].set_xlabel("Aqueous Solute Mass Fraction ($X$ - Feed)")
    axes[1, 0].set_ylabel("Organic Solute Mass Fraction ($Y$ - Extract)")
    axes[1, 0].set_xlim([0, max_limit])
    axes[1, 0].set_ylim([0, max_limit])
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].grid(True, linestyle=':', alpha=0.6)

    # Panel 4: Water Mass Fractions Across Stages
    axes[1, 1].plot(sim_df['Stage'], sim_df['Feed_Water'], marker='o', color='teal', label='Feed Water')
    axes[1, 1].plot(sim_df['Stage'], sim_df['Extract_Water'], marker='s', color='orange', label='Extract Water')
    axes[1, 1].set_title("Carrier Fluid (Water) Mass Fractions", fontweight='bold')
    axes[1, 1].set_ylabel("Mass Fraction")
    axes[1, 1].set_ylim([0, 1.0])
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(True, linestyle=':', alpha=0.6)

    # Panel 5: Di-Ether Mass Fractions Across Stages
    axes[2, 0].plot(sim_df['Stage'], sim_df['Feed_Ether'], marker='o', color='purple', label='Feed Di-Ether')
    axes[2, 0].plot(sim_df['Stage'], sim_df['Extract_Ether'], marker='s', color='brown', label='Extract Di-Ether')
    axes[2, 0].set_title("Solvent (Di-Ether) Mass Fractions", fontweight='bold')
    axes[2, 0].set_xlabel("Extraction Stage")
    axes[2, 0].set_ylabel("Mass Fraction")
    axes[2, 0].set_ylim([0, 1.0])
    axes[2, 0].legend(fontsize=8)
    axes[2, 0].grid(True, linestyle=':', alpha=0.6)  # <-- Fixed bracket here

    # Hide unused 6th subplot
    axes[2, 1].axis('off')

    plt.tight_layout()
    plot_filename = "aspen_range_distribution_dashboard.png"
    plt.savefig(plot_filename, dpi=300)
    print(f"\n[✔] Dashboard with background training envelope saved successfully as '{plot_filename}'.")
    plt.show()
    
except ValueError as e:
    print(f"\n❌ SIMULATION REJECTED:\n{e}")