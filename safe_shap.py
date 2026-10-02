import joblib
import pandas as pd
import numpy as np
import os
import sys

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "rf_aml.pkl")
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "transactions_ml.csv")
OUT_PATH = os.path.join(PROJECT_ROOT, "models", "shap_data_safe.pkl")

print("--- Generating Explanations ---")

try:
    # 1. Load Model and Data
    print("Loading model...")
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model not found at {MODEL_PATH}")
        sys.exit(1)
        
    model = joblib.load(MODEL_PATH)
    
    print("Loading data...")
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: Data not found at {DATA_PATH}")
        sys.exit(1)
        
    df = pd.read_csv(DATA_PATH)

    # 2. Identify Features
    # We use the model's internal feature names to ensure 100% match
    if hasattr(model, "feature_names_in_"):
        feature_cols = list(model.feature_names_in_)
    else:
        # Fallback if model doesn't store names (older sklearn versions)
        print("Warning: Model missing feature_names_in_, guessing columns...")
        feature_cols = [c for c in df.columns if c not in ['txn_id', 'timestamp', 'from_acc', 'to_acc', 'narrative', 'label', 'ml_pred_prob']]

    print(f"Model expects {len(feature_cols)} features.")
    X = df[feature_cols]

    # 3. Attempt SHAP Generation
    # We prioritize 'Proxy SHAP' (Simplified) because it is faster and never crashes
    # for student projects. Real TreeSHAP can be brittle with version mismatches.
    print("Calculating Feature Contributions (Proxy Method)...")
    
    importances = model.feature_importances_
    med = X.median().values
    X_np = X.values
    
    # Calculate simplified SHAP: (Value - Median) * Importance
    # This tells us: "This feature is high/low, and that matters X amount"
    shap_values = []
    for row in X_np:
        direction = np.sign(row - med)
        # Avoid zero direction for matching median
        direction[direction == 0] = 1 
        shap_row = importances * np.abs(row - med) * direction
        shap_values.append(shap_row)

    shap_values = np.array(shap_values)

    # 4. Save the Result
    # Structure: (type, shap_values, X_data, importances, median, feature_names)
    data_to_save = ("proxy_shap", shap_values, X, importances, med, feature_cols)
    
    joblib.dump(data_to_save, OUT_PATH)
    print(f" Success! Explanation data saved to {OUT_PATH}")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()