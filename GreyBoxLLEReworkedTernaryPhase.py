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
        
        stages = pd.to_numeric(sub_df[10], errors='coerce')
        temps = pd.to_numeric(sub_df[11], errors='coerce')
        flow_feed = pd.to_numeric(sub_df[14], errors='coerce')
        flow_solv = pd.to_numeric(sub_df[15], errors='coerce')
        
        w_feed_water = pd.to_numeric(sub_df[18], errors='coerce')
        w_feed_ether = pd.to_numeric(sub_df[19], errors='coerce')
        w_feed_solute = pd.to_numeric(sub_df[20], errors='coerce')
        w_extr_water = pd.to_numeric(sub_df[23], errors='coerce')
        w_extr_ether = pd.to_numeric(sub_df[24], errors='coerce')
        w_extr_solute = pd.to_numeric(sub_df[25], errors='coerce')

        stage_data = pd.DataFrame({
            'Stage': stages, 'Temperature': temps, 'Feed_Flow': flow_feed, 'Solvent_Flow': flow_solv,
            'Feed_Water': w_feed_water, 'Feed_Ether': w_feed_ether, 'Feed_Solute': w_feed_solute,
            'Extract_Water': w_extr_water, 'Extract_Ether': w_extr_ether, 'Extract_Solute': w_extr_solute
        }).dropna()
        aggregated_rows.append(stage_data)
    except Exception:
        continue

master_df = pd.concat(aggregated_rows, ignore_index=True)

# 2. Train multi-output estimators for ternary branches
features = ['Stage', 'Temperature', 'Feed_Flow', 'Solvent_Flow']
X_train = master_df[features].values
targets = ['Feed_Water', 'Feed_Ether', 'Feed_Solute', 'Extract_Water', 'Extract_Ether', 'Extract_Solute']

models = {}
for col in targets:
    y_train = master_df[col].values
    m = RandomForestRegressor(n_estimators=100, random_state=42)
    m.fit(X_train, y_train)
    models[col] = m

# 3. Compute Numerical Performance Metrics (R² and RMSE) for Ternary Variables
comparison_metrics = []
for col in targets:
    y_true = master_df[col].values
    y_pred = models[col].predict(X_train)
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    comparison_metrics.append({
        'Phase Component Target': col, 
        'R² Score': round(r2, 4), 
        'RMSE': f"{rmse:.5e}"
    })

metrics_df = pd.DataFrame(comparison_metrics)

print("\n" + "="*65)
print("     TABLE 2: SURROGATE MODEL VALIDATION PERFORMANCE (TERNARY)")
print("="*65)
print(metrics_df.to_string(index=False))
print("="*65)
metrics_df.to_csv("ternary_model_validation_metrics.csv", index=False)

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
        simulated_scenarios.append({
            'Scenario': scn,
            'Stage': stage_idx,
            'Extract_Water': models['Extract_Water'].predict(sample_input)[0],
            'Extract_Ether': models['Extract_Ether'].predict(sample_input)[0],
            'Extract_Solute': models['Extract_Solute'].predict(sample_input)[0],
        })

sim_results_df = pd.DataFrame(simulated_scenarios)

# 5. Mathematical transformation function to Gibbs Triangle coordinates
def transform_to_ternary(water, solvent, solute):
    total = water + solvent + solute + 1e-9
    w = water / total
    s = solvent / total
    u = solute / total
    x = 0.5 * (2.0 * s + u)
    y = (np.sqrt(3.0) / 2.0) * u
    return x, y

# 6. Visual Plot: Ternary Phase Diagram
plt.figure(figsize=(10, 9))
verts = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2], [0, 0]])
plt.plot(verts[:, 0], verts[:, 1], color='black', lw=2)

plt.text(-0.05, -0.04, "Solvent Branch\n(Di-Ether Phase)", fontsize=10, fontweight='bold', ha='center')
plt.text(1.05, -0.04, "Diluent Branch\n(Water Phase)", fontsize=10, fontweight='bold', ha='center')
plt.text(0.5, np.sqrt(3)/2 + 0.03, "Solute\n(Propionic Acid 100%)", fontsize=10, fontweight='bold', ha='center')

train_x_feed, train_y_feed = transform_to_ternary(master_df['Feed_Water'].values, master_df['Feed_Ether'].values, master_df['Feed_Solute'].values)
train_x_extr, train_y_extr = transform_to_ternary(master_df['Extract_Water'].values, master_df['Extract_Ether'].values, master_df['Extract_Solute'].values)

plt.scatter(train_x_feed, train_y_feed, color='lightgray', s=18, alpha=0.5, label='Historical Feed/Raffinate Branch')
plt.scatter(train_x_extr, train_y_extr, color='darkgray', s=18, alpha=0.5, label='Historical Extract Branch')

sim_x, sim_y = transform_to_ternary(sim_results_df['Extract_Water'].values, sim_results_df['Extract_Ether'].values, sim_results_df['Extract_Solute'].values)
plt.scatter(sim_x, sim_y, color='darkviolet', s=28, alpha=0.8, label='Monte Carlo Random Scenarios (25x)')

plt.title("Chemically Grounded Monte Carlo: Gibbs Ternary Diagram", fontsize=13, fontweight='bold', pad=20)
plt.axis('off')
plt.legend(loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig("monte_carlo_chemically_grounded_ternary.png", dpi=300)
print("\n[✔] Ternary phase diagram and validation metrics successfully generated.")
plt.show()