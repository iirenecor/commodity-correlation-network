import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

#asset definition
tickers = [
    # Grains
    'ZC=F', 'ZW=F', 'ZS=F', 'ZM=F', 'ZL=F', 'ZO=F', 'ZR=F',
    # Softs
    'KC=F', 'CC=F', 'SB=F', 'CT=F', 'OJ=F', 'LBS=F',
    # Livestock
    'LE=F', 'GF=F', 'HE=F',
    # Energy
    'CL=F', 'BZ=F', 'NG=F', 'RB=F', 'HO=F',
    # Metals
    'GC=F', 'SI=F', 'HG=F', 'PL=F', 'PA=F', 'ALI=F'
]

#download and data filtering
data = yf.download(tickers, start='2010-01-01', end='2025-12-31')['Close']
data = data.dropna()

print(data.head())
print(f"Filas: {data.shape[0]}, Activos: {data.shape[1]}")

# daily returns
returns = data.pct_change().dropna()

# correlation matrix
correlation_matrix = returns.corr()

print(correlation_matrix.round(2))

#data dictionary
real_names = {
    'ZC=F': 'Corn', 'ZW=F': 'Wheat', 'ZS=F': 'Soybeans', 'ZM=F': 'Soybean Meal',
    'ZL=F': 'Soybean Oil', 'ZO=F': 'Oats', 'ZR=F': 'Rice',
    'KC=F': 'Coffee', 'CC=F': 'Cocoa', 'SB=F': 'Sugar', 'CT=F': 'Cotton', 
    'OJ=F': 'Orange Juice', 'LBS=F': 'Lumber',
    'LE=F': 'Live Cattle', 'GF=F': 'Feeder Cattle', 'HE=F': 'Lean Hogs',
    'CL=F': 'Crude Oil (WTI)', 'BZ=F': 'Crude Oil (Brent)', 'NG=F': 'Natural Gas', 
    'RB=F': 'Gasoline', 'HO=F': 'Heating Oil',
    'GC=F': 'Gold', 'SI=F': 'Silver', 'HG=F': 'Copper', 'PL=F': 'Platinum', 
    'PA=F': 'Palladium', 'ALI=F': 'Aluminum'
}

import networkx as nx

categories = {
    'ZC=F': 'Grains', 'ZW=F': 'Grains', 'ZS=F': 'Grains', 'ZM=F': 'Grains',
    'ZL=F': 'Grains', 'ZO=F': 'Grains', 'ZR=F': 'Grains',
    'KC=F': 'Softs', 'CC=F': 'Softs', 'SB=F': 'Softs', 'CT=F': 'Softs', 
    'OJ=F': 'Softs', 'LBS=F': 'Softs',
    'LE=F': 'Livestock', 'GF=F': 'Livestock', 'HE=F': 'Livestock',
    'CL=F': 'Energy', 'BZ=F': 'Energy', 'NG=F': 'Energy', 'RB=F': 'Energy', 'HO=F': 'Energy',
    'GC=F': 'Metals', 'SI=F': 'Metals', 'HG=F': 'Metals', 'PL=F': 'Metals', 
    'PA=F': 'Metals', 'ALI=F': 'Metals'
}

color_map = {
    'Grains': "#000000", 'Softs': "#000000", 'Livestock': "#000000",
    'Energy': "#000000", 'Metals': "#000000"
}

#correlation graph
G = nx.Graph()
threshold = 0.01

for i in range(len(correlation_matrix.columns)):
    for j in range(i+1, len(correlation_matrix.columns)):
        ticker_i = correlation_matrix.columns[i]
        ticker_j = correlation_matrix.columns[j]
        corr = correlation_matrix.iloc[i, j]
        if abs(corr) > threshold:
            G.add_edge(ticker_i, ticker_j, weight=corr)

for t in correlation_matrix.columns:
    if t not in G.nodes():
        G.add_node(t)
        
        
        node_colors = [color_map[categories[node]] for node in G.nodes()]

plt.figure(figsize=(14, 10))
pos = nx.spring_layout(G, k=0.6, seed=42)
plt.gcf().set_facecolor("#FFFFFF")

nx.draw_networkx_nodes(G, pos, node_color="#000000", node_size=80)

labels = {node: real_names[node] for node in G.nodes()}
label_pos = {k: (v[0], v[1] + 0.06) for k, v in pos.items()}

for node, (x, y) in label_pos.items():
    plt.text(x, y, labels[node], fontsize=12, fontweight='bold',
              color=color_map[categories[node]], ha='center', va='center')

edges = G.edges()
weights = [G[u][v]['weight'] for u, v in edges]

edges_drawn = nx.draw_networkx_edges(G, pos, edge_color=weights, 
                                       edge_cmap=plt.cm.coolwarm,
                                       width=[w*8 for w in weights], 
                                       alpha=0.8)

plt.colorbar(edges_drawn, label='Correlation Strength')



plt.title('Commodity Correlation Network (2010–2025)', fontsize=15, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.savefig('commodity_network.png', dpi=150, bbox_inches='tight', facecolor="#FFFFFF")
plt.show()

#correlation heatmap
plt.figure(figsize=(14, 12))
plt.imshow(correlation_matrix, cmap='coolwarm', aspect='auto')
plt.colorbar(label='Correlation')

pos = nx.spring_layout(G, k=0.6, seed=42)
plt.gcf().set_facecolor("#FFFFFF")

labels_list = [real_names[t] for t in correlation_matrix.columns]
plt.xticks(range(len(correlation_matrix.columns)), labels_list, rotation=90)
plt.yticks(range(len(correlation_matrix.columns)), labels_list)

plt.title('Commodity Correlation Matrix (2010–2025)', fontsize=15, fontweight='bold',)
plt.tight_layout()
plt.savefig('correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()


# annualized volatility
volatility = returns.std() * np.sqrt(252)

vol_df = pd.DataFrame({
    'Ticker': volatility.index,
    'Volatility': volatility.values,
    'Name': [real_names[t] for t in volatility.index],
    'Category': [categories[t] for t in volatility.index]
})

vol_df = vol_df.sort_values('Volatility', ascending=True)
bar_colors = [color_map[cat] for cat in vol_df['Category']]

plt.figure(figsize=(10, 12))
plt.barh(vol_df['Name'], vol_df['Volatility'], color=bar_colors)

plt.xlabel('Annualized Volatility', fontsize=11)
plt.title('Commodity Volatility by Category (2010–2025)', fontsize=15, fontweight='bold')

import matplotlib.patches as mpatches
legend_patches = [mpatches.Patch(color=c, label=cat) for cat, c in color_map.items()]
plt.legend(handles=legend_patches, loc='lower right', fontsize=10)

plt.tight_layout()
plt.savefig('commodity_volatility.png', dpi=150, bbox_inches='tight')
plt.show()

#intra- inter-correlation
plt.figure(figsize=(8, 6))
intra_corrs = []
inter_corrs = []

for i in range(len(correlation_matrix.columns)):
    for j in range(i+1, len(correlation_matrix.columns)):
        t1, t2 = correlation_matrix.columns[i], correlation_matrix.columns[j]
        corr = correlation_matrix.iloc[i, j]
        if categories[t1] == categories[t2]:
            intra_corrs.append(corr)
        else:
            inter_corrs.append(corr)
plt.boxplot([intra_corrs, inter_corrs], tick_labels=['Intra-category', 'Inter-category'])
plt.ylabel('Correlation')
plt.title('Intra-category vs Inter-category Correlation', fontsize=14, fontweight='bold')
plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('intra_vs_inter_correlation.png', dpi=150, bbox_inches='tight')
plt.show()