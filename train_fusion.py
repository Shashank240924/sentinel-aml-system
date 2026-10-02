import pandas as pd
import joblib
import os
from xgboost import XGBClassifier  # <--- NEW IMPORT
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def train_meta_model():
    print("[INFO] Loading engine outputs...")
    
    # 1. Load Data (Safety Logic)
    if not os.path.exists("data/transactions_graph.csv"):
        raise FileNotFoundError("Missing data/transactions_graph.csv. Run graph_analysis.py first.")
    
    df = pd.read_csv("data/transactions_graph.csv")

    # Safety Check: Merge behavior if missing
    if 'behavior_risk' not in df.columns:
        print("[WARN] Merging behavior risk...")
        if not os.path.exists("data/transactions_behavior.csv"):
             raise FileNotFoundError("Missing data/transactions_behavior.csv. Run behavior.py first.")
        
        df_beh = pd.read_csv("data/transactions_behavior.csv")
        df = df.merge(df_beh[['from_acc', 'timestamp', 'behavior_risk']], 
                      on=['from_acc', 'timestamp'], how='left')
        df['behavior_risk'] = df['behavior_risk'].fillna(0)
    
    # Calculate Rule Risk
    df['rule_risk'] = 0.0
    df.loc[df['amount'] > 20000, 'rule_risk'] = 0.4
    df.loc[df['amount'] > 50000, 'rule_risk'] = 0.8
    
    # Ensure Label Exists
    if 'label' not in df.columns:
        print("[WARN] 'label' missing. merging from synthetic source...")
        df_raw = pd.read_csv("data/synthetic_transactions.csv")
        df['label'] = df_raw['label']

    feature_cols = ['graph_risk', 'behavior_risk', 'rule_risk']
    X = df[feature_cols].fillna(0)
    y = df['label']

    # 2. TRAIN XGBOOST (The Upgrade)
    print("[INFO] Training XGBoost Meta-Model...")
    
    # scale_pos_weight is crucial for Fraud (Imbalanced Data)
    # It tells the model: "Pay more attention to the rare fraud cases"
    model = XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=4,
        scale_pos_weight=5,  # Helps with class imbalance
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    model.fit(X, y)

    # 3. EVALUATE & SHOW IMPORTANCE
    # Note: XGBoost uses feature_importances_, not coef_
    importances = model.feature_importances_
    
    print("\n[RESULT] XGBoost Feature Importance:")
    print(f"Graph Risk:     {importances[0]:.4f}")
    print(f"Behavior Risk:  {importances[1]:.4f}")
    print(f"Rule Risk:      {importances[2]:.4f}")
    
    if importances[0] > importances[1]:
        print(">> Insight: The Network Graph is your strongest predictor.")
    else:
        print(">> Insight: Behavioral Patterns are your strongest predictor.")

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/meta_fusion_model.pkl")
    print("\n[SUCCESS] XGBoost Model saved to models/meta_fusion_model.pkl")

if __name__ == "__main__":
    train_meta_model()