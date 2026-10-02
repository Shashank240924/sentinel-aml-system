import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder

# Make sure folders exist
os.makedirs("data", exist_ok=True)

def load_data(path="data\\synthetic_transactions.csv"):
    df = pd.read_csv(path, parse_dates=['timestamp'])
    return df

def basic_features(df):
    # Extract time features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_transfer'] = (df['txn_type'] == 'transfer').astype(int)

    # Encode categorical columns
    for col in ['merchant', 'country', 'channel', 'txn_type']:
        le = LabelEncoder()
        df[col + '_enc'] = le.fit_transform(df[col].astype(str))

    return df

def aggregate_features(df):
    # Aggregate stats per user
    agg = df.groupby('from_acc')['amount'].agg(['mean', 'std', 'count']).reset_index()
    agg = agg.rename(columns={'mean': 'acc_avg_amount', 'std': 'acc_std_amount', 'count': 'acc_txn_count'})
    df = df.merge(agg, on='from_acc', how='left')
    df['acc_std_amount'] = df['acc_std_amount'].fillna(0)
    return df

if __name__ == "__main__":
    df = load_data()
    df = basic_features(df)
    df = aggregate_features(df)
    df.to_csv("data\\transactions_features.csv", index=False)
    print(f"Saved transactions_features.csv with shape {df.shape}")
