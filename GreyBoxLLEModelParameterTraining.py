import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_score, cross_val_predict
from sklearn.metrics import r2_score, mean_squared_error

# 1. Load the new multi-sheet Excel file
excel_path = r"C:\Users\ddzob\Downloads\CFD extractiedata Dennis TvH.xlsx"
xls = pd.ExcelFile(excel_path)

# Filter out non-scenario metadata sheets like 'Blad1'
scenario_sheets = [s for s in xls.sheet_names if s != 'Blad1']
print(f"Discovered {len(scenario_sheets)} scenario sheets in the workbook.")

# 2. Automatically aggregate data across all scenario sheets
combined_data = []
for sheet in scenario_sheets:
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
        max_col = df.shape[1] - 1
        k_col = max_col if max_col in [27, 30] else 30
        if k_col >= df.shape[1]:
            k_col = df.shape[1] - 1
            
        sub_df = df.iloc[3:].copy()
        stage = pd.to_numeric(sub_df[10], errors='coerce')
        temp = pd.to_numeric(sub_df[11], errors='coerce')
        flow1 = pd.to_numeric(sub_df[14], errors='coerce')
        flow2 = pd.to_numeric(sub_df[15], errors='coerce')
        k_val = pd.to_numeric(sub_df[k_col], errors='coerce')
        
        temp_df = pd.DataFrame({
            'Stage': stage,
            'Temperature': temp,
            '1st liquid flow': flow1,
            '2nd liquid flow': flow2,
            'K_solute': k_val
        }).dropna()
        
        combined_data.append(temp_df)
    except Exception as e:
        print(f"Skipping sheet {sheet} due to read error: {e}")

merged_df = pd.concat(combined_data, ignore_index=True)
print(f"Successfully compiled total experimental rows: {len(merged_df)}")

# 3. Define Feature Matrix (X) and Target (y)
X = merged_df[['Temperature', '1st liquid flow', '2nd liquid flow']].values
y = merged_df['K_solute'].values

# 4. Initialize Random Forest Model & K-Fold Cross-Validation
model = RandomForestRegressor(n_estimators=100, random_state=42)
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Perform 5-fold cross validation for R² scores and MSE
cv_r2_scores = cross_val_score(model, X, y, cv=kf, scoring='r2')
cv_mse_scores = -cross_val_score(model, X, y, cv=kf, scoring='neg_mean_squared_error')

mean_r2 = cv_r2_scores.mean()
mean_mse = cv_mse_scores.mean()

print(f"\n--- Cross-Validation Metrics (5-Fold) ---")
print(f"Mean R² Score: {mean_r2:.4f} (Scores across folds: {np.round(cv_r2_scores, 3)})")
print(f"Mean Squared Error (MSE): {mean_mse:.6f}")

# Generate cross-validated predictions for plotting against actuals
y_pred_cv = cross_val_predict(model, X, y, cv=kf)

# 5. Log Performance to Persistent CSV Tracker
log_file = "model_performance_log.csv"
run_data = pd.DataFrame({
    "Run_Timestamp": [pd.Timestamp.now()],
    "R2_Score": [mean_r2],
    "MSE": [mean_mse],
    "Dataset_Rows": [len(merged_df)]
})

if os.path.exists(log_file):
    history_df = pd.read_csv(log_file)
    history_df = pd.concat([history_df, run_data], ignore_index=True)
else:
    history_df = run_data

history_df.to_csv(log_file, index=False)
print(f"Performance log updated. Total recorded script executions: {len(history_df)}")

# 6. Data Visualization Dashboard
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Cross-Validated Predictions vs Actual Values
axes[0].scatter(y, y_pred_cv, color='darkorange', edgecolors='k', s=60, alpha=0.7, label='CV Predictions')
axes[0].plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2, label='Ideal Fit (y = x)')
axes[0].set_title("Cross-Validated Model vs. CFD Synthetic Data", fontsize=12, fontweight='bold')
axes[0].set_xlabel("Actual K_Solute (CFD Excel)", fontsize=10)
axes[0].set_ylabel("Predicted K_Solute (Grey-Box Twin)", fontsize=10)
axes[0].legend()
axes[0].grid(True, linestyle=':', alpha=0.6)

# Plot 2: Historical Cross-Validated R² Accuracy Over Sequential Runs
axes[1].plot(history_df.index + 1, history_df['R2_Score'], marker='s', color='teal', lw=2, markersize=6)
axes[1].set_title("Historical CV R² Accuracy Across Runs", fontsize=12, fontweight='bold')
axes[1].set_xlabel("Run Iteration", fontsize=10)
axes[1].set_ylabel("Mean R² Score", fontsize=10)
axes[1].set_ylim([min(0, history_df['R2_Score'].min() - 0.1), 1.05])
axes[1].grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()

# Save dashboard figure locally
plot_filename = "model_performance_dashboard.png"
plt.savefig(plot_filename, dpi=300)
print(f"Dashboard visualization updated and saved as '{plot_filename}'.")

# Show the plot window
plt.show()