import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, recall_score, precision_score
import joblib

os.makedirs("models", exist_ok=True)
os.makedirs("data", exist_ok=True)

def apply_rule_based_flags(df):
    """Add smarter heuristic features."""
    # 1. Velocity: Rolling count of txns in short window (simulated by last 5 rows per user)
    df['velocity_count'] = df.groupby('from_acc')['amount'].transform(lambda x: x.rolling(window=5, min_periods=1).count())
    df['velocity_sum'] = df.groupby('from_acc')['amount'].transform(lambda x: x.rolling(window=5, min_periods=1).sum())
    
    # 2. Smurfing: High frequency + Low amount
    df['smurf_risk'] = ((df['velocity_count'] > 4) & (df['amount'] < 10000)).astype(int)
    
    # 3. Mule Risk: Sudden flow larger than usual average
    # Handle division by zero safely
    avg_amt = df['acc_avg_amount'].replace(0, 1) 
    df['mule_risk'] = (df['velocity_sum'] > (avg_amt * 3)).astype(int)

    # 4. Standard flags
    risky_countries = ['RU', 'NG', 'AE', 'UA']
    df['risky_country_flag'] = df['country'].isin(risky_countries).astype(int)
    df['high_amount_flag'] = (df['amount'] > 9000).astype(int) # kept for legacy
    
    # Composite Rule Score
    df['rule_risk'] = (
        0.3 * df['smurf_risk'] +
        0.3 * df['mule_risk'] +
        0.2 * df['risky_country_flag'] +
        0.2 * df['high_amount_flag']
    ).clip(0, 1)
    
    return df

def train_hybrid_model():
    print("Loading data...")
    df = pd.read_csv("data\\transactions_graph.csv", parse_dates=['timestamp'])

    print("Feature Engineering...")
    df = apply_rule_based_flags(df)

    # Fill NaNs created by rolling windows
    df = df.fillna(0)

    feature_cols = [
        'amount', 'hour', 'day_of_week', 'is_transfer',
        'merchant_enc', 'country_enc', 'channel_enc', 'txn_type_enc',
        'acc_avg_amount', 'acc_std_amount', 'acc_txn_count',
        'behavior_risk', 'graph_risk',
        'rule_risk', 'smurf_risk', 'mule_risk', 'velocity_count'
    ]

    X = df[feature_cols]
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    print("Training Random Forest...")
    model = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42, class_weight='balanced', n_jobs=-1)
    model.fit(X_train, y_train)

    joblib.dump(model, "models\\rf_aml.pkl")
    print("Model saved to models\\rf_aml.pkl")

    # Evaluation
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    
    print("\n---  MODEL PERFORMANCE ---")
    print(f"Accuracy:  {model.score(X_test, y_test):.4f}")
    print(f"Precision: {precision_score(y_test, preds):.4f}")
    print(f"Recall:    {recall_score(y_test, preds):.4f} (Crucial for AML)")
    print(f"ROC-AUC:   {roc_auc_score(y_test, probs):.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, preds))

    # Save predictions
    df['ml_pred_prob'] = model.predict_proba(X)[:, 1]
    df.to_csv("data\\transactions_ml.csv", index=False)
    print("Saved data\\transactions_ml.csv")
    # ... after printing confusion matrix ...

    # NEW: Save Feature Importance Plot
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    feature_imp = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False).head(10)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=feature_imp, y=feature_imp.index, hue=feature_imp.index, palette="viridis", legend=False)
    plt.title("Top 10 Key Risk Drivers (Model Logic)")
    plt.xlabel("Importance Score")
    plt.tight_layout()
    plt.savefig("models/feature_importance.png")
    print("Saved models/feature_importance.png (Great for your Project Report!)")

if __name__ == "__main__":
    train_hybrid_model()