import pandas as pd
import joblib
import os
import numpy as np

def fuse_risk_scores_dynamic():
    print("[INFO] Starting Dynamic Risk Fusion...")
    
    # 1. LOAD DATA
    # FIX: We load ONLY transactions_graph.csv because it already contains 
    # both graph_risk and behavior_risk from the previous step.
    df = pd.read_csv("data\\transactions_graph.csv")
    
    # 2. CALCULATE RULE RISK
    # (Must match the logic used in training)
    df['rule_risk'] = 0.0
    df.loc[df['amount'] > 20000, 'rule_risk'] = 0.4
    df.loc[df['amount'] > 50000, 'rule_risk'] = 0.8
    
    # 3. LOAD THE BRAIN
    model_path = "models\\meta_fusion_model.pkl"
    if not os.path.exists(model_path):
        raise FileNotFoundError("Model missing! You must run train_fusion.py first.")
    
    print(f"[INFO] Loading model from {model_path}...")
    model = joblib.load(model_path)
    
    # 4. MAKE PREDICTIONS
    feature_cols = ['graph_risk', 'behavior_risk', 'rule_risk']
    
    # Check for missing columns to be safe
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}. Check graph_analysis.py output.")
        
    X_input = df[feature_cols].fillna(0)
    
    # Get the probability of fraud (Class 1)
    df['total_risk'] = model.predict_proba(X_input)[:, 1]

    # 5. FLAG AND SAVE
    # Flag transactions with > 75% fraud probability
    df['flagged'] = (df['total_risk'] >= 0.75).astype(int)
    
    output_path = "data\\transactions_final.csv"
    df_sorted = df.sort_values('total_risk', ascending=False)
    df_sorted.to_csv(output_path, index=False)
    
    print(f"[SUCCESS] Processed {len(df)} transactions.")
    print(f"[SUCCESS] Saved results to {output_path}")
    print("Top 3 Riskiest Transactions:")
    print(df_sorted[['txn_id', 'total_risk', 'graph_risk', 'behavior_risk']].head(3))

if __name__ == "__main__":
    fuse_risk_scores_dynamic()