import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

# Ensure 'data' folder exists
os.makedirs("data", exist_ok=True)

def generate_transactions(n_accounts=200, n_txns=1000, start_date="2024-01-01"):
    np.random.seed(42)
    random.seed(42)
    accounts = [f"A{100000+i}" for i in range(n_accounts)]
    start = datetime.fromisoformat(start_date)
    rows = []
    merchant_cats = [
        'Amazon', 'Walmart', 'Netflix', 'Uber', 'Starbucks', 'Apple Store', 
        'Pharmacy', 'Shell Gas', 'Airbnb', 'Spotify', 'Target', 'McDonalds'
    ]
    countries = ['IN','US','GB','NG','CN','AE','RU','UA']
    channels = ['online','branch','atm','mobile']

    # 1. Generate Basic "Normal" Transactions (~85%)
    for i in range(int(n_txns * 0.85)):
        t = start + timedelta(seconds=int(np.random.exponential(scale=3600*4)))
        acc = random.choice(accounts)
        txn_type = np.random.choice(['deposit','withdrawal','transfer','payment'], p=[0.15,0.15,0.45,0.25])
        
        # Normal amounts: Log-normal distribution
        amount = float(np.round(np.random.lognormal(mean=3.5, sigma=1.0), 2))
        
        to_acc = None
        if txn_type == 'transfer':
            to_acc = random.choice(accounts)
            while to_acc == acc: to_acc = random.choice(accounts)

        rows.append({
            'txn_id': "", # Placeholder, filled later
            'timestamp': t,
            'from_acc': acc, 'to_acc': to_acc,
            'txn_type': txn_type, 'amount': amount,
            'merchant': random.choice(merchant_cats),
            'country': random.choice(countries),
            'channel': random.choice(channels),
            'narrative': 'normal transaction',
            'label': 0 
        })
        start = t

    # 2. Inject "Smurfing" (Structuring) - Splitting large sums
    num_smurfs = 10 
    for _ in range(num_smurfs):
        launderer = random.choice(accounts)
        receiver = random.choice(accounts)
        total_sum = np.random.uniform(20000, 50000)
        n_chunks = np.random.randint(5, 12)
        chunk_amt = round(total_sum / n_chunks, 2)
        base_time = start + timedelta(days=np.random.randint(0, 10))
        
        for k in range(n_chunks):
            rows.append({
                'txn_id': "",
                'timestamp': base_time + timedelta(hours=k*2, minutes=random.randint(1,30)),
                'from_acc': launderer, 'to_acc': receiver,
                'txn_type': 'transfer', 'amount': chunk_amt,
                'merchant': 'remittance', 'country': 'IN', 'channel': 'online',
                'narrative': 'smurfing sequence',
                'label': 1
            })

    # 3. Inject "Money Mule" Rings (Fan-In -> Fan-Out)
    num_mule_rings = 5
    for _ in range(num_mule_rings):
        mule = random.choice(accounts)
        kingpin = random.choice(accounts)
        senders = random.sample([a for a in accounts if a != mule and a != kingpin], k=5)
        base_time = start + timedelta(days=np.random.randint(5, 20))
        
        # Fan-In
        collected_amt = 0
        for s in senders:
            amt = np.random.uniform(2000, 8000)
            collected_amt += amt
            rows.append({
                'txn_id': "",
                'timestamp': base_time + timedelta(minutes=random.randint(10, 120)),
                'from_acc': s, 'to_acc': mule,
                'txn_type': 'transfer', 'amount': round(amt, 2),
                'merchant': 'transfer', 'country': 'US', 'channel': 'mobile',
                'narrative': 'mule layering in',
                'label': 1
            })
            
        # Fan-Out
        rows.append({
            'txn_id': "",
            'timestamp': base_time + timedelta(hours=3),
            'from_acc': mule, 'to_acc': kingpin,
            'txn_type': 'transfer', 'amount': round(collected_amt * 0.95, 2),
            'merchant': 'transfer', 'country': 'AE', 'channel': 'mobile',
            'narrative': 'mule layering out',
            'label': 1
        })

    # Sort and add IDs
    df = pd.DataFrame(rows).sort_values('timestamp').reset_index(drop=True)
    df['txn_id'] = [f"T{i:07d}" for i in range(len(df))]
    
    return df

if __name__ == "__main__":
    df = generate_transactions(n_accounts=200, n_txns=1000)
    df.to_csv("data\\synthetic_transactions.csv", index=False)
    print(f" Saved synthetic_transactions.csv with shape {df.shape}")