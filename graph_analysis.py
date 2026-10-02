import pandas as pd
import networkx as nx
import numpy as np
import os

# ensure data directory exists
os.makedirs("data", exist_ok=True)

def build_transaction_graph(df):
    """Build a directed graph from account-to-account transactions."""
    G = nx.DiGraph()
    df_transfers = df.dropna(subset=['to_acc'])

    for _, row in df_transfers.iterrows():
        a, b, amt = row['from_acc'], row['to_acc'], float(row['amount'])
        if G.has_edge(a, b):
            G[a][b]['weight'] += amt
            G[a][b]['count'] += 1
        else:
            G.add_edge(a, b, weight=amt, count=1)
    return G

def compute_graph_features(df, G):
    """Compute centrality & clustering metrics, then derive a risk score."""
    # Compute metrics safely even for small graphs
    pr = nx.pagerank(G, alpha=0.85)
    deg_in = dict(G.in_degree())
    deg_out = dict(G.out_degree())
    und = G.to_undirected()
    clustering = nx.clustering(und)

    # Map metrics back to each transaction
    df['pagerank'] = df['from_acc'].map(pr).fillna(0.0)
    df['deg_in'] = df['from_acc'].map(deg_in).fillna(0)
    df['deg_out'] = df['from_acc'].map(deg_out).fillna(0)
    df['clustering'] = df['from_acc'].map(clustering).fillna(0.0)

    # Normalize and compute overall risk
    df['graph_risk'] = (
        0.6 * df['pagerank'] +
        0.2 * (df['deg_in'] + df['deg_out']) / (df['deg_in'] + df['deg_out']).max() +
        0.2 * df['clustering']
    )

    # Normalize 0–1
    df['graph_risk'] = (
        (df['graph_risk'] - df['graph_risk'].min()) /
        (df['graph_risk'].max() - df['graph_risk'].min() + 1e-9)
    )

    return df

if __name__ == "__main__":
    print("Loading transactions_behavior.csv ...")
    df = pd.read_csv("data\\transactions_behavior.csv", parse_dates=['timestamp'])

    print("Building transaction graph ...")
    G = build_transaction_graph(df)
    print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    print("Computing graph features and risk scores ...")
    df = compute_graph_features(df, G)

    # save the new dataset
    df.to_csv("data\\transactions_graph.csv", index=False)
    print(f"Saved transactions_graph.csv with shape {df.shape}")

    # Optionally preview top 5 risky accounts
    risky = df.sort_values('graph_risk', ascending=False).head(5)
    print("\nTop 5 high-risk accounts based on network analysis:")
    print(risky[['from_acc', 'graph_risk']].drop_duplicates().head(5))
