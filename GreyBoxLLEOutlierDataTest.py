# import pandas as pd
# import numpy as np
# import os
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import KFold, cross_val_score, cross_val_predict
# from sklearn.metrics import r2_score, mean_squared_error

# # 1. Load the comprehensive CFD multi-sheet workbook
# excel_path = r"C:\Users\ddzob\Downloads\CFD extractiedata Dennis TvH.xlsx"
# xls = pd.ExcelFile(excel_path)
# scenario_sheets = [s for s in xls.sheet_names if s != 'Blad1']
# print(f"Loading and parsing {len(scenario_sheets)} operational scenario sheets...")

# # 2. Extract Stage-by-Stage Parameters across all tabs
# aggregated_rows = []
# for sheet in scenario_sheets:
#     try:
#         df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
#         sub_df = df.iloc[3:].copy()
        
#         # Extract features & targets per stage
#         stages = pd.to_numeric(sub_df[10], errors='coerce')
#         temps = pd.to_numeric(sub_df[11], errors='coerce')
#         pressures = pd.to_numeric(sub_df[12], errors='coerce')
#         flow_feed = pd.to_numeric(sub_df[14], errors='coerce')      # 1st liquid flow (Feed)
#         flow_solvent = pd.to_numeric(sub_df[15], errors='coerce')   # 2nd liquid flow (Solvent / DI-ETHER)
        
#         # Compositions Liquid 1 & Liquid 2 (WATER, DI-ETHER, PROPI-01)
#         w_feed_water = pd.to_numeric(sub_df[17], errors='coerce')
#         w_feed_ether = pd.to_numeric(sub_df[18], errors='coerce')
#         w_feed_solute = pd.to_numeric(sub_df[19], errors='coerce')
        
#         w_extr_water = pd.to_numeric(sub_df[23], errors='coerce')
#         w_extr_ether = pd.to_numeric(sub_df[24], errors='coerce')
#         w_extr_solute = pd.to_numeric(sub_df[25], errors='coerce')
        
#         # K-values (Partition coefficients)
#         k_solute = pd.to_numeric(sub_df[30], errors='coerce')

#         stage_data = pd.DataFrame({
#             'Sheet': sheet,
#             'Stage': stages,
#             'Temperature': temps,
#             'Pressure': pressures,
#             'Feed_Flow': flow_feed,
#             'Solvent_Flow': flow_solvent,
#             'Feed_Solute_Comp': w_feed_solute,
#             'Extract_Solute_Comp': w_extr_solute,
#             'K_Solute': k_solute
#         }).dropna()
        
#         aggregated_rows.append(stage_data)
#     except Exception as e:
#         continue

# master_df = pd.concat(aggregated_rows, ignore_index=True)
# print(f"Successfully compiled {len(master_df)} stage-level data points across all runs.")

# # ==========================================
# # 3. Define Gray-Box Model Architecture
# # ==========================================
# # Inputs (Reduced State Vector): Operating conditions & stage progression
# X = master_df[['Stage', 'Temperature', 'Feed_Flow', 'Solvent_Flow']].values
# # Target to predict: Solute Partition Coefficient (K_Solute) & Phase Compositions
# y_k = master_df['K_Solute'].values
# y_comp = master_df['Extract_Solute_Comp'].values

# # Train Random Forest Black-Box Estimators for Equilibrium Mapping
# model_k = RandomForestRegressor(n_estimators=100, random_state=42)
# model_comp = RandomForestRegressor(n_estimators=100, random_state=42)

# kf = KFold(n_splits=5, shuffle=True, random_state=42)

# # Evaluate Cross-Validation Performance
# r2_k = cross_val_score(model_k, X, y_k, cv=kf, scoring='r2').mean()
# r2_comp = cross_val_score(model_comp, X, y_comp, cv=kf, scoring='r2').mean()

# print(f"\n--- Digital Twin Validation Scores (5-Fold CV) ---")
# print(f"K-Value Prediction R² Score: {r2_k:.4f}")
# print(f"Extract Composition Prediction R² Score: {r2_comp:.4f}")

# # Fit final models on full dataset
# model_k.fit(X, y_k)
# model_comp.fit(X, y_comp)

# # ==========================================
# # 4. Simulate an Extraction Column Profile (e.g., 5 Stages)
# # ==========================================
# print("\n--- Simulating Extraction Column Stage Profile ---")
# sim_temp = 40.0         # Operating Temperature [°C]
# sim_feed_flow = 105.0   # Feed flow rate [kg/hr]
# sim_solv_flow = 250.0   # Solvent (DI-ETHER) flow rate [kg/hr]

# print(f"Operating Conditions -> Temp: {sim_temp}°C | Feed Flow: {sim_feed_flow} kg/hr | Solvent Flow: {sim_solv_flow} kg/hr\n")
# print(f"{'Stage':<8} | {'Pred K_Solute':<15} | {'Pred Extract Solute Comp':<25}")
# print("-" * 55)

# for stage_idx in range(1, 6):
#     sample_input = np.array([[stage_idx, sim_temp, sim_feed_flow, sim_solv_flow]])
#     pred_k = model_k.predict(sample_input)[0]
#     pred_comp = model_comp.predict(sample_input)[0]
#     print(f"{stage_idx:<8} | {pred_k:<15.4f} | {pred_comp:<25.4f}")

# import pandas as pd
# import numpy as np
# import os
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import KFold, cross_val_score, cross_val_predict
# from sklearn.metrics import r2_score, mean_squared_error

# # 1. Load the updated multi-sheet Excel workbook
# excel_path = r"C:\Users\ddzob\Downloads\CFD extractiedata Dennis TvH (1).xlsx"
# xls = pd.ExcelFile(excel_path)
# scenario_sheets = [s for s in xls.sheet_names if s != 'Blad1']
# print(f"Discovered {len(scenario_sheets)} scenario sheets in the updated workbook.")

# # 2. Automatically parse and aggregate data across all scenario sheets
# aggregated_rows = []
# for sheet in scenario_sheets:
#     try:
#         df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
#         sub_df = df.iloc[3:].copy()
#         max_col = df.shape[1] - 1
        
#         # Determine K-value column based on sheet structure (col 30 or derived fallback)
#         k_col = 30 if max_col >= 30 else (27 if max_col >= 27 else None)
        
#         stages = pd.to_numeric(sub_df[10], errors='coerce')
#         temps = pd.to_numeric(sub_df[11], errors='coerce')
#         pressures = pd.to_numeric(sub_df[12], errors='coerce')
#         flow_feed = pd.to_numeric(sub_df[14], errors='coerce')     # FEED flow (1st liquid)
#         flow_solv = pd.to_numeric(sub_df[15], errors='coerce')     # DI-ETHER flow (2nd liquid)
        
#         # Compositions under Liquid 1 (FEED side) and Liquid 2 (DI-ETHER / EXTR side)
#         w_feed_solute = pd.to_numeric(sub_df[19], errors='coerce') # PROPI-01 in liquid 1
#         w_extr_solute = pd.to_numeric(sub_df[25], errors='coerce') # PROPI-01 in liquid 2
        
#         if k_col is not None and k_col < df.shape[1]:
#             k_solute = pd.to_numeric(sub_df[k_col], errors='coerce')
#         else:
#             k_solute = w_extr_solute / (w_feed_solute + 1e-9)

#         stage_data = pd.DataFrame({
#             'Sheet': sheet,
#             'Stage': stages,
#             'Temperature': temps,
#             'Pressure': pressures,
#             'Feed_Flow': flow_feed,
#             'Solvent_Flow': flow_solv,
#             'Feed_Solute_Comp': w_feed_solute,
#             'Extract_Solute_Comp': w_extr_solute,
#             'K_Solute': k_solute
#         }).dropna()
        
#         aggregated_rows.append(stage_data)
#     except Exception as e:
#         continue

# master_df = pd.concat(aggregated_rows, ignore_index=True)
# print(f"Successfully compiled {len(master_df)} stage-level data points from the new file.")

# # ==========================================
# # 3. Train Gray-Box ML & Validate via K-Fold CV
# # ==========================================
# X = master_df[['Stage', 'Temperature', 'Feed_Flow', 'Solvent_Flow']].values
# y_k = master_df['K_Solute'].values
# y_comp = master_df['Extract_Solute_Comp'].values

# model_k = RandomForestRegressor(n_estimators=100, random_state=42)
# model_comp = RandomForestRegressor(n_estimators=100, random_state=42)

# kf = KFold(n_splits=5, shuffle=True, random_state=42)
# r2_k = cross_val_score(model_k, X, y_k, cv=kf, scoring='r2').mean()
# r2_comp = cross_val_score(model_comp, X, y_comp, cv=kf, scoring='r2').mean()

# print(f"\n--- Updated Digital Twin Validation Scores (5-Fold CV) ---")
# print(f"K-Value Prediction R² Score: {r2_k:.4f}")
# print(f"Extract Solute Composition R² Score: {r2_comp:.4f}")

# # Fit models on full dataset
# model_k.fit(X, y_k)
# model_comp.fit(X, y_comp)

# # ==========================================
# # 4. Simulate an Extraction Column Profile
# # ==========================================
# print("\n--- Simulating Column Stage Profile with New Data ---")
# sim_temp = 20.1         # Operating Temperature [°C]
# sim_feed_flow = 130.0   # Feed flow rate [kg/hr]
# sim_solv_flow = 150.0   # DI-ETHER solvent flow rate [kg/hr]

# print(f"Operating Conditions -> Temp: {sim_temp}°C | Feed Flow: {sim_feed_flow} kg/hr | DI-ETHER Flow: {sim_solv_flow} kg/hr\n")
# print(f"{'Stage':<8} | {'Pred K_Solute':<15} | {'Pred Extract Solute Comp':<25}")
# print("-" * 55)

# for stage_idx in range(1, 6):
#     sample_input = np.array([[stage_idx, sim_temp, sim_feed_flow, sim_solv_flow]])
#     pred_k = model_k.predict(sample_input)[0]
#     pred_comp = model_comp.predict(sample_input)[0]
#     print(f"{stage_idx:<8} | {pred_k:<15.4f} | {pred_comp:<25.4f}")




# import pandas as pd
# import numpy as np
# import os
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import KFold, cross_val_score

# # 1. Load the updated multi-sheet Excel workbook
# excel_path = r"C:\Users\ddzob\Downloads\CFD extractiedata Dennis TvH (1).xlsx"
# xls = pd.ExcelFile(excel_path)
# scenario_sheets = [s for s in xls.sheet_names if s != 'Blad1']

# # 2. Extract comprehensive parameters per stage across all sheets
# aggregated_rows = []
# for sheet in scenario_sheets:
#     try:
#         df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
#         sub_df = df.iloc[3:].copy()
#         max_col = df.shape[1] - 1
#         k_col = 30 if max_col >= 30 else (27 if max_col >= 27 else None)
        
#         stages = pd.to_numeric(sub_df[10], errors='coerce')
#         temps = pd.to_numeric(sub_df[11], errors='coerce')
#         pressures = pd.to_numeric(sub_df[12], errors='coerce')
#         flow_feed = pd.to_numeric(sub_df[14], errors='coerce')
#         flow_solv = pd.to_numeric(sub_df[15], errors='coerce')
        
#         # Compositions Liquid 1 (FEED side)
#         w_feed_water = pd.to_numeric(sub_df[17], errors='coerce')
#         w_feed_ether = pd.to_numeric(sub_df[18], errors='coerce')
#         w_feed_solute = pd.to_numeric(sub_df[19], errors='coerce')
        
#         # Compositions Liquid 2 (DI-ETHER / EXTR side)
#         w_extr_water = pd.to_numeric(sub_df[23], errors='coerce')
#         w_extr_ether = pd.to_numeric(sub_df[24], errors='coerce')
#         w_extr_solute = pd.to_numeric(sub_df[25], errors='coerce')
        
#         if k_col is not None and k_col < df.shape[1]:
#             k_solute = pd.to_numeric(sub_df[k_col], errors='coerce')
#         else:
#             k_solute = w_extr_solute / (w_feed_solute + 1e-9)

#         stage_data = pd.DataFrame({
#             'Stage': stages,
#             'Temperature': temps,
#             'Pressure': pressures,
#             'Feed_Flow': flow_feed,
#             'Solvent_Flow': flow_solv,
#             'Feed_Water': w_feed_water,
#             'Feed_Ether': w_feed_ether,
#             'Feed_Solute': w_feed_solute,
#             'Extract_Water': w_extr_water,
#             'Extract_Ether': w_extr_ether,
#             'Extract_Solute': w_extr_solute,
#             'K_Solute': k_solute
#         }).dropna()
        
#         aggregated_rows.append(stage_data)
#     except Exception as e:
#         continue

# master_df = pd.concat(aggregated_rows, ignore_index=True)

# # 3. Train multi-output estimators for each target parameter
# features = ['Stage', 'Temperature', 'Feed_Flow', 'Solvent_Flow']
# X = master_df[features].values

# targets = ['Pressure', 'Feed_Water', 'Feed_Ether', 'Feed_Solute', 
#            'Extract_Water', 'Extract_Ether', 'Extract_Solute', 'K_Solute']

# models = {}
# kf = KFold(n_splits=5, shuffle=True, random_state=42)

# print("\n--- Training Multi-Parameter Gray-Box Models ---")
# for target in targets:
#     y = master_df[target].values
#     model = RandomForestRegressor(n_estimators=100, random_state=42)
#     model.fit(X, y)
#     models[target] = model
#     r2 = cross_val_score(model, X, y, cv=kf, scoring='r2').mean()
#     print(f"Target [{target:<15}] -> 5-Fold R² Score: {r2:.4f}")

# # ==========================================
# # 4. Simulate Full Column Profile (Stages 1 to 10)
# # ==========================================
# print("\n" + "="*80)
# print("FULL COLUMN SIMULATION PROFILE (10 STAGES)")
# print("="*80)

# sim_temp = 20.1
# sim_feed_flow = 130.0
# sim_solv_flow = 150.0

# simulation_records = []
# for stage_idx in range(1, 11):
#     sample_input = np.array([[stage_idx, sim_temp, sim_feed_flow, sim_solv_flow]])
    
#     row_data = {
#         'Stage': stage_idx,
#         'Temperature': sim_temp,
#         'Feed_Flow': sim_feed_flow,
#         'Solvent_Flow': sim_solv_flow
#     }
#     for target in targets:
#         row_data[target] = models[target].predict(sample_input)[0]
    
#     simulation_records.append(row_data)

# sim_df = pd.DataFrame(simulation_records)

# # Print clean summary table to console
# print(sim_df[['Stage', 'Pressure', 'Feed_Solute', 'Extract_Solute', 'K_Solute']].to_string(index=False))

# # Save detailed simulation run to a persistent CSV file
# output_csv = "full_column_simulation_profile.csv"
# sim_df.to_csv(output_csv, index=False)
# print(f"\nDetailed multi-parameter profile saved successfully to '{output_csv}'.")










# import pandas as pd
# import numpy as np
# import os
# import matplotlib.pyplot as plt  # <--- THIS WAS MISSING
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import KFold, cross_val_score

# # 1. Load the updated multi-sheet Excel workbook
# excel_path = r"C:\Users\ddzob\Downloads\CFD extractiedata Dennis TvH (1).xlsx"
# xls = pd.ExcelFile(excel_path)
# scenario_sheets = [s for s in xls.sheet_names if s != 'Blad1']

# # 2. Extract comprehensive parameters per stage across all sheets
# aggregated_rows = []
# for sheet in scenario_sheets:
#     try:
#         df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
#         sub_df = df.iloc[3:].copy()
#         max_col = df.shape[1] - 1
#         k_col = 30 if max_col >= 30 else (27 if max_col >= 27 else None)
        
#         stages = pd.to_numeric(sub_df[10], errors='coerce')
#         temps = pd.to_numeric(sub_df[11], errors='coerce')
#         pressures = pd.to_numeric(sub_df[12], errors='coerce')
#         flow_feed = pd.to_numeric(sub_df[14], errors='coerce')
#         flow_solv = pd.to_numeric(sub_df[15], errors='coerce')
        
#         # Compositions Liquid 1 (FEED side) & Liquid 2 (EXTRACT / DI-ETHER side)
#         # w_feed_water = pd.to_numeric(sub_df[17], errors='coerce')
#         # w_feed_ether = pd.to_numeric(sub_df[18], errors='coerce')
#         # w_feed_solute = pd.to_numeric(sub_df[19], errors='coerce')
        
#         # w_extr_water = pd.to_numeric(sub_df[23], errors='coerce')
#         # w_extr_ether = pd.to_numeric(sub_df[24], errors='coerce')
#         # w_extr_solute = pd.to_numeric(sub_df[25], errors='coerce')

#         # Compositions Liquid 1 (FEED side) & Liquid 2 (EXTRACT / DI-ETHER side)
#         # Note: Index 17 is the Stage column for Liquid 1; Water is actually at index 18 (or adjust based on sheet structure)
#         # Let's use robust column mapping:
#         w_feed_water = pd.to_numeric(sub_df[18], errors='coerce')  # Corrected to WATER column for Liquid 1
#         w_feed_ether = pd.to_numeric(sub_df[19], errors='coerce')
#         w_feed_solute = pd.to_numeric(sub_df[20], errors='coerce')
        
#         w_extr_water = pd.to_numeric(sub_df[23], errors='coerce')
#         w_extr_ether = pd.to_numeric(sub_df[24], errors='coerce')
#         w_extr_solute = pd.to_numeric(sub_df[25], errors='coerce')
        
#         if k_col is not None and k_col < df.shape[1]:
#             k_solute = pd.to_numeric(sub_df[k_col], errors='coerce')
#         else:
#             k_solute = w_extr_solute / (w_feed_solute + 1e-9)

#         stage_data = pd.DataFrame({
#             'Stage': stages,
#             'Temperature': temps,
#             'Pressure': pressures,
#             'Feed_Flow': flow_feed,
#             'Solvent_Flow': flow_solv,
#             'Feed_Water': w_feed_water,
#             'Feed_Ether': w_feed_ether,
#             'Feed_Solute': w_feed_solute,
#             'Extract_Water': w_extr_water,
#             'Extract_Ether': w_extr_ether,
#             'Extract_Solute': w_extr_solute,
#             'K_Solute': k_solute
#         }).dropna()
        
#         aggregated_rows.append(stage_data)
#     except Exception as e:
#         continue

# master_df = pd.concat(aggregated_rows, ignore_index=True)

# # 3. Train multi-output estimators for each target parameter
# features = ['Stage', 'Temperature', 'Feed_Flow', 'Solvent_Flow']
# X = master_df[features].values

# targets = ['Pressure', 'Feed_Water', 'Feed_Ether', 'Feed_Solute', 
#            'Extract_Water', 'Extract_Ether', 'Extract_Solute', 'K_Solute']

# models = {}
# kf = KFold(n_splits=5, shuffle=True, random_state=42)

# print("\n--- Training Multi-Parameter Gray-Box Models ---")
# for target in targets:
#     y = master_df[target].values
#     model = RandomForestRegressor(n_estimators=100, random_state=42)
#     model.fit(X, y)
#     models[target] = model
#     r2 = cross_val_score(model, X, y, cv=kf, scoring='r2').mean()
#     print(f"Target [{target:<15}] -> 5-Fold R² Score: {r2:.4f}")

# # ==========================================
# # 4. Simulate Full Column Profile (Stages 1 to 10)
# # ==========================================
# print("\n" + "="*80)
# print("FULL COLUMN SIMULATION PROFILE (10 STAGES)")
# print("="*80)

# sim_temp = 5.0
# sim_feed_flow = 130.0
# sim_solv_flow = 147.0

# simulation_records = []
# for stage_idx in range(1, 11):
#     sample_input = np.array([[stage_idx, sim_temp, sim_feed_flow, sim_solv_flow]])
    
#     row_data = {
#         'Stage': stage_idx,
#         'Temperature': sim_temp,
#         'Feed_Flow': sim_feed_flow,
#         'Solvent_Flow': sim_solv_flow
#     }
#     for target in targets:
#         row_data[target] = models[target].predict(sample_input)[0]
    
#     simulation_records.append(row_data)

# sim_df = pd.DataFrame(simulation_records)

# # Print clean summary table to console
# print(sim_df[['Stage', 'Pressure', 'Feed_Solute', 'Extract_Solute', 'K_Solute']].to_string(index=False))

# # Save detailed simulation run to a persistent CSV file
# output_csv = "full_column_simulation_profile.csv"
# sim_df.to_csv(output_csv, index=False)
# print(f"\nDetailed multi-parameter profile saved successfully to '{output_csv}'.")

# # ==========================================
# # 5. Generate Multi-Panel Visual Graph Dashboard (Corrected Scaling)
# # ==========================================
# fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# # Subplot 1: Solute Concentration Profile across Stages
# axes[0, 0].plot(sim_df['Stage'], sim_df['Feed_Solute'], marker='o', color='crimson', label='Feed Solute (Liquid 1)')
# axes[0, 0].plot(sim_df['Stage'], sim_df['Extract_Solute'], marker='s', color='dodgerblue', label='Extract Solute (Liquid 2)')
# axes[0, 0].set_title("Solute Concentration Profile (Propionic Acid)", fontweight='bold')
# axes[0, 0].set_xlabel("Extraction Stage")
# axes[0, 0].set_ylabel("Mass Fraction")
# axes[0, 0].set_ylim([0, 1.0])  # Locked physically valid scale
# axes[0, 0].legend()
# axes[0, 0].grid(True, linestyle=':', alpha=0.6)

# # Subplot 2: Partition Coefficient (K_Solute) across Stages
# axes[0, 1].plot(sim_df['Stage'], sim_df['K_Solute'], marker='^', color='forestgreen', lw=2)
# axes[0, 1].set_title("Partition Coefficient Profile ($K_D$)", fontweight='bold')
# axes[0, 1].set_xlabel("Extraction Stage")
# axes[0, 1].set_ylabel("Distribution Ratio ($K$)")
# axes[0, 1].grid(True, linestyle=':', alpha=0.6)

# # Subplot 3: Phase Water Compositions across Stages (Strictly 0 to 1)
# axes[1, 0].plot(sim_df['Stage'], sim_df['Feed_Water'], marker='o', color='teal', label='Feed Water')
# axes[1, 0].plot(sim_df['Stage'], sim_df['Extract_Water'], marker='s', color='orange', label='Extract Water')
# axes[1, 0].set_title("Water Mass Fractions Across Stages", fontweight='bold')
# axes[1, 0].set_xlabel("Extraction Stage")
# axes[1, 0].set_ylabel("Mass Fraction")
# axes[1, 0].set_ylim([0, 1.0])  # Locked physically valid scale
# axes[1, 0].legend()
# axes[1, 0].grid(True, linestyle=':', alpha=0.6)

# # Subplot 4: Phase DI-ETHER (Solvent) Compositions across Stages
# axes[1, 1].plot(sim_df['Stage'], sim_df['Feed_Ether'], marker='o', color='purple', label='Feed Di-Ether')
# axes[1, 1].plot(sim_df['Stage'], sim_df['Extract_Ether'], marker='s', color='brown', label='Extract Di-Ether')
# axes[1, 1].set_title("Di-Ether Mass Fractions Across Stages", fontweight='bold')
# axes[1, 1].set_xlabel("Extraction Stage")
# axes[1, 1].set_ylabel("Mass Fraction")
# axes[1, 1].set_ylim([0, 1.0])  # Locked physically valid scale
# axes[1, 1].legend()
# axes[1, 1].grid(True, linestyle=':', alpha=0.6)

# plt.tight_layout()

# plot_filename = "full_column_simulation_plots.png"
# plt.savefig(plot_filename, dpi=300)
# print(f"Visual graph dashboard saved successfully as '{plot_filename}'.")
# plt.show()




# import pandas as pd
# import numpy as np
# import os
# import matplotlib.pyplot as plt
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import KFold, cross_val_score

# # 1. Load the updated multi-sheet Excel workbook
# excel_path = r"C:\Users\ddzob\Downloads\CFD extractiedata Dennis TvH (1).xlsx"
# xls = pd.ExcelFile(excel_path)
# scenario_sheets = [s for s in xls.sheet_names if s != 'Blad1']

# # 2. Extract comprehensive parameters per stage across all sheets
# aggregated_rows = []
# for sheet in scenario_sheets:
#     try:
#         df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
#         sub_df = df.iloc[3:].copy()
#         max_col = df.shape[1] - 1
#         k_col = 30 if max_col >= 30 else (27 if max_col >= 27 else None)
        
#         stages = pd.to_numeric(sub_df[10], errors='coerce')
#         temps = pd.to_numeric(sub_df[11], errors='coerce')
#         pressures = pd.to_numeric(sub_df[12], errors='coerce')
#         flow_feed = pd.to_numeric(sub_df[14], errors='coerce')
#         flow_solv = pd.to_numeric(sub_df[15], errors='coerce')
        
#         # Compositions Liquid 1 & Liquid 2
#         w_feed_water = pd.to_numeric(sub_df[18], errors='coerce')
#         w_feed_ether = pd.to_numeric(sub_df[19], errors='coerce')
#         w_feed_solute = pd.to_numeric(sub_df[20], errors='coerce')
        
#         w_extr_water = pd.to_numeric(sub_df[23], errors='coerce')
#         w_extr_ether = pd.to_numeric(sub_df[24], errors='coerce')
#         w_extr_solute = pd.to_numeric(sub_df[25], errors='coerce')
        
#         if k_col is not None and k_col < df.shape[1]:
#             k_solute = pd.to_numeric(sub_df[k_col], errors='coerce')
#         else:
#             k_solute = w_extr_solute / (w_feed_solute + 1e-9)

#         stage_data = pd.DataFrame({
#             'Stage': stages,
#             'Temperature': temps,
#             'Pressure': pressures,
#             'Feed_Flow': flow_feed,
#             'Solvent_Flow': flow_solv,
#             'Feed_Water': w_feed_water,
#             'Feed_Ether': w_feed_ether,
#             'Feed_Solute': w_feed_solute,
#             'Extract_Water': w_extr_water,
#             'Extract_Ether': w_extr_ether,
#             'Extract_Solute': w_extr_solute,
#             'K_Solute': k_solute
#         }).dropna()
        
#         aggregated_rows.append(stage_data)
#     except Exception as e:
#         continue

# master_df = pd.concat(aggregated_rows, ignore_index=True)

# # 3. Train multi-output estimators
# features = ['Stage', 'Temperature', 'Feed_Flow', 'Solvent_Flow']
# X = master_df[features].values

# targets = ['Pressure', 'Feed_Water', 'Feed_Ether', 'Feed_Solute', 
#            'Extract_Water', 'Extract_Ether', 'Extract_Solute', 'K_Solute']

# models = {}
# kf = KFold(n_splits=5, shuffle=True, random_state=42)

# print("\n--- Training Multi-Parameter Gray-Box Models ---")
# for target in targets:
#     y = master_df[target].values
#     model = RandomForestRegressor(n_estimators=100, random_state=42)
#     model.fit(X, y)
#     models[target] = model

# # # ==========================================
# # # 4. Outlier & Extrapolation Test Suite
# # # ==========================================
# # print("\n" + "="*80)
# # print("OUTLIER & EXTRAPOLATION TEST SUITE")
# # print("="*80)

# # # Test cases provided in the screenshot
# # test_cases = [
# #     {"test_id": 1, "temp": 5.0,   "solvent": 400.0, "desc": "Extreme Low Temp / High Solvent (Outlier)"},
# #     {"test_id": 2, "temp": 110.0, "solvent": 100.0, "desc": "Extreme High Temp / Low Solvent (Outlier)"},
# #     {"test_id": 3, "temp": 24.0,  "solvent": 255.0, "desc": "Standard Operating Range"},
# #     {"test_id": 4, "temp": 42.0,  "solvent": 201.0, "desc": "Standard Operating Range"},
# #     {"test_id": 5, "temp": 59.0,  "solvent": 230.0, "desc": "Standard Operating Range"}
# # ]

# # standard_feed_flow = 130.0  # Baseline feed flow for testing

# # for case in test_cases:
# #     print(f"\nTest Case {case['test_id']}: {case['desc']}")
# #     print(f"Inputs -> Temp: {case['temp']}°C | Solvent Flow: {case['solvent']} kg/hr")
# #     print(f"{'Stage':<8} | {'Pred Extract Solute':<20} | {'Pred K_Solute':<15}")
# #     print("-" * 50)
    
# #     # Simulate Stage 1 and Stage 5 for each test case
# #     for stage_idx in [1, 5]:
# #         sample_input = np.array([[stage_idx, case['temp'], standard_feed_flow, case['solvent']]])
# #         pred_comp = models['Extract_Solute'].predict(sample_input)[0]
# #         pred_k = models['K_Solute'].predict(sample_input)[0]
# #         print(f"{stage_idx:<8} | {pred_comp:<20.4f} | {pred_k:<15.4f}")

# # print("\n" + "="*80)


# # ==========================================
# # 4. Outlier & Extrapolation Test Suite (All 10 Stages)
# # ==========================================
# print("\n" + "="*85)
# print("OUTLIER & EXTRAPOLATION TEST SUITE (FULL 10-STAGE PROFILES)")
# print("="*85)

# # Test cases provided by your coach
# coach_test_cases = [
#     {"test_id": 1, "temp": 5.0,   "solvent": 400.0, "desc": "Extreme Low Temp / High Solvent (Outlier)"},
#     {"test_id": 2, "temp": 110.0, "solvent": 100.0, "desc": "Extreme High Temp / Low Solvent (Outlier)"},
#     {"test_id": 3, "temp": 24.0,  "solvent": 255.0, "desc": "Standard Operating Range"},
#     {"test_id": 4, "temp": 42.0,  "solvent": 201.0, "desc": "Standard Operating Range"},
#     {"test_id": 5, "temp": 59.0,  "solvent": 230.0, "desc": "Standard Operating Range"}
# ]

# standard_feed_flow = 130.0  # Baseline feed flow rate [kg/hr]

# for case in coach_test_cases:
#     print(f"\nTest Case {case['test_id']}: {case['desc']}")
#     print(f"Inputs -> Temp: {case['temp']}°C | Solvent Flow: {case['solvent']} kg/hr | Feed Flow: {standard_feed_flow} kg/hr")
#     print("-" * 75)
#     print(f"{'Stage':<6} | {'Feed Solute':<13} | {'Extract Solute':<15} | {'K_Solute':<12} | {'Extract Water':<14}")
#     print("-" * 75)
    
#     # Loop across ALL 10 stages for the current test case
#     for stage_idx in range(1, 11):
#         sample_input = np.array([[stage_idx, case['temp'], standard_feed_flow, case['solvent']]])
        
#         pred_feed_solute = models['Feed_Solute'].predict(sample_input)[0]
#         pred_extr_solute = models['Extract_Solute'].predict(sample_input)[0]
#         pred_k = models['K_Solute'].predict(sample_input)[0]
#         pred_extr_water = models['Extract_Water'].predict(sample_input)[0]
        
#         print(f"{stage_idx:<6} | {pred_feed_solute:<13.4f} | {pred_extr_solute:<15.4f} | {pred_k:<12.4f} | {pred_extr_water:<14.4f}")

# print("\n" + "="*85)










import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold

# 1. Load the updated multi-sheet Excel workbook
excel_path = r"C:\Users\ddzob\Downloads\CFD extractiedata Dennis TvH (1).xlsx"
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
            'Stage': stages,
            'Temperature': temps,
            'Pressure': pressures,
            'Feed_Flow': flow_feed,
            'Solvent_Flow': flow_solv,
            'Feed_Water': w_feed_water,
            'Feed_Ether': w_feed_ether,
            'Feed_Solute': w_feed_solute,
            'Extract_Water': w_extr_water,
            'Extract_Ether': w_extr_ether,
            'Extract_Solute': w_extr_solute,
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

# ==========================================
# 4. Coach's Outlier & Extrapolation Visual Test Suite
# ==========================================
print("\n" + "="*85)
print("GENERATING COACH'S TEST SUITE COMPARISON PLOTS...")
print("="*85)

coach_test_cases = [
    {"test_id": 1, "temp": 5.0,   "solvent": 400.0, "label": "5°C, 400 kg/h (Outlier)"},
    {"test_id": 2, "temp": 110.0, "solvent": 100.0, "label": "110°C, 100 kg/h (Outlier)"},
    {"test_id": 3, "temp": 24.0,  "solvent": 255.0, "label": "24°C, 255 kg/h"},
    {"test_id": 4, "temp": 42.0,  "solvent": 201.0, "label": "42°C, 201 kg/h"},
    {"test_id": 5, "temp": 59.0,  "solvent": 230.0, "label": "59°C, 230 kg/h"}
]

standard_feed_flow = 130.0

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
linestyles = ['-', '--', '-.', ':', '-']
colors = ['firebrick', 'darkorange', 'forestgreen', 'dodgerblue', 'purple']

for i, case in enumerate(coach_test_cases):
    stages = np.arange(1, 11)
    extr_solutes, k_solutes, water_extrs, ether_extrs = [], [], [], []
    
    for s in stages:
        inp = np.array([[s, case['temp'], standard_feed_flow, case['solvent']]])
        extr_solutes.append(models['Extract_Solute'].predict(inp)[0])
        k_solutes.append(models['K_Solute'].predict(inp)[0])
        water_extrs.append(models['Extract_Water'].predict(inp)[0])
        ether_extrs.append(models['Extract_Ether'].predict(inp)[0])
        
    lbl = case['label']
    ls = linestyles[i]
    col = colors[i]
    
    axes[0, 0].plot(stages, extr_solutes, marker='o', linestyle=ls, color=col, label=lbl)
    axes[0, 1].plot(stages, k_solutes, marker='^', linestyle=ls, color=col, label=lbl)
    axes[1, 0].plot(stages, water_extrs, marker='s', linestyle=ls, color=col, label=lbl)
    axes[1, 1].plot(stages, ether_extrs, marker='d', linestyle=ls, color=col, label=lbl)

# Format Subplots
axes[0, 0].set_title("Extract Solute Concentration Comparison", fontweight='bold')
axes[0, 0].set_xlabel("Extraction Stage")
axes[0, 0].set_ylabel("Mass Fraction")
axes[0, 0].grid(True, linestyle=':', alpha=0.6)
axes[0, 0].legend(fontsize=8)

axes[0, 1].set_title("Partition Coefficient ($K_D$) Comparison", fontweight='bold')
axes[0, 1].set_xlabel("Extraction Stage")
axes[0, 1].set_ylabel("Distribution Ratio ($K$)")
axes[0, 1].grid(True, linestyle=':', alpha=0.6)
axes[0, 1].legend(fontsize=8)

axes[1, 0].set_title("Extract Water Mass Fraction Comparison", fontweight='bold')
axes[1, 0].set_xlabel("Extraction Stage")
axes[1, 0].set_ylabel("Mass Fraction")
axes[1, 0].set_ylim([0, 0.1])
axes[1, 0].grid(True, linestyle=':', alpha=0.6)
axes[1, 0].legend(fontsize=8)

axes[1, 1].set_title("Extract Di-Ether Mass Fraction Comparison", fontweight='bold')
axes[1, 1].set_xlabel("Extraction Stage")
axes[1, 1].set_ylabel("Mass Fraction")
axes[1, 1].set_ylim([0, 1.0])
axes[1, 1].grid(True, linestyle=':', alpha=0.6)
axes[1, 1].legend(fontsize=8)

plt.tight_layout()
plot_filename = "coach_test_cases_comparison.png"
plt.savefig(plot_filename, dpi=300)
print(f"Comparison dashboard saved successfully as '{plot_filename}'.")
plt.show()