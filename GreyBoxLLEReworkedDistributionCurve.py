import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error

# 1. Load the multi-sheet Excel workbook
excel_path = r"C:\Users\ddzob\Downloads\CFD extractiedata Dennis TvH (3).xlsx"
xls = pd.ExcelFile(excel_path)
scenario_sheets = [s for s in xls.sheet_names if s != 'Blad1']

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
    except Exception:
        continue

master_df = pd.concat(aggregated_rows, ignore_index=True)

# 2. Train multi-output estimators
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

# 3. Compute Numerical Performance Metrics (R² and RMSE)
comparison_metrics = []
for target in targets:
    y_true = master_df[target].values
    y_pred = models[target].predict(X)
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    comparison_metrics.append({
        'Target Variable': target, 
        'R² Score': round(r2, 4), 
        'RMSE': f"{rmse:.5e}"
    })

metrics_df = pd.DataFrame(comparison_metrics)

print("\n" + "="*65)
print("   TABLE 1: SURROGATE MODEL VALIDATION PERFORMANCE (DISTRIBUTION)")
print("="*65)
print(metrics_df.to_string(index=False))
print("="*65)
metrics_df.to_csv("distribution_model_validation_metrics.csv", index=False)

# 4. Automated 25-Scenario Monte Carlo Simulation
# np.random.seed(42)
num_scenarios = 25
simulated_scenarios = []

for scn in range(1, num_scenarios + 1):
    rand_temp = np.random.uniform(10.0, 65.0)
    rand_solvent = np.random.uniform(88.0, 400.0)
    rand_feed = np.random.uniform(80.0, 140.0)
    
    for stage_idx in range(1, 11):
        sample_input = np.array([[stage_idx, rand_temp, rand_feed, rand_solvent]])
        row_data = {'Scenario': scn, 'Stage': stage_idx}
        for target in targets:
            row_data[target] = models[target].predict(sample_input)[0]
        simulated_scenarios.append(row_data)

sim_results_df = pd.DataFrame(simulated_scenarios)

# 5. Visual Plot: Distribution Curve ($Y$ vs $X$)
plt.figure(figsize=(10, 8))
train_x = master_df['Feed_Solute'].values
train_y = master_df['Extract_Solute'].values
plt.scatter(train_x, train_y, color='lightgray', s=20, alpha=0.6, label='Historical Training Scenarios (Aspen)')

sim_x = sim_results_df['Feed_Solute'].values
sim_y = sim_results_df['Extract_Solute'].values
plt.scatter(sim_x, sim_y, color='darkviolet', s=30, alpha=0.7, label='Monte Carlo Random Scenarios (25x)')

max_limit = max(max(train_x), max(train_y)) * 1.1
plt.plot([0, max_limit], [0, max_limit], color='gray', linestyle='--', label='45° Reference ($Y=X$)')

plt.title("Monte Carlo Benchmark: Phase Equilibrium Distribution ($Y$ vs $X$)", fontsize=13, fontweight='bold')
plt.xlabel("Aqueous Solute Mass Fraction ($X$ - Feed)", fontsize=11)
plt.ylabel("Organic Solute Mass Fraction ($Y$ - Extract)", fontsize=11)
plt.xlim([0, max_limit])
plt.ylim([0, max_limit])
plt.legend(fontsize=10)
plt.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.savefig("monte_carlo_distribution_comparison.png", dpi=300)
print("\n[✔] Distribution plot and validation metrics successfully generated.")
plt.show()