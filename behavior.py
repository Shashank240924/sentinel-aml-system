import pandas as pd
import numpy as np
import os

# Ensure folder exists
os.makedirs("data", exist_ok=True)

def build_user_profiles(df):
    """Create per-account statistics (normal behavior baseline)."""
    profiles = df.groupby('from_acc').agg(
        prof_avg_amount=('amount', 'mean'),
        prof_std_amount=('amount', 'std'),
        prof_txn_count=('amount', 'count'),
        prof_unique_to=('to_acc', pd.Series.nunique)
    ).reset_index()
    profiles['prof_std_amount'] = profiles['prof_std_amount'].fillna(0)
    return profiles

def compute_behavior_risk(df, profiles):
    """Merge per-user profiles and calculate behavioral deviation."""
    # Merge with suffixes to avoid name clashes
    df = df.merge(profiles, on='from_acc', how='left')

    # Compute deviation (z-score)
    df['z_score'] = (df['amount'] - df['prof_avg_amount']) / (df['prof_std_amount'] + 1e-6)
    df['behavior_risk'] = df['z_score'].abs().clip(0, 10) / 10.0
    df['behavior_risk'] = df['behavior_risk'].fillna(0.0)

    return df

if __name__ == "__main__":
    print("Loading transactions_features.csv ...")
    df = pd.read_csv("data\\transactions_features.csv", parse_dates=['timestamp'])

    print("Building user profiles ...")
    profiles = build_user_profiles(df)
    print(f"Profiles built for {profiles.shape[0]} accounts")

    print("Computing behavior risk ...")
    df = compute_behavior_risk(df, profiles)

    # Save results
    df.to_csv("data\\transactions_behavior.csv", index=False)
    profiles.to_csv("data\\user_profiles.csv", index=False)

    print(f" Saved transactions_behavior.csv with shape {df.shape}")
    print(f" Saved user_profiles.csv with shape {profiles.shape}")
