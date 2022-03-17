import matplotlib.pyplot as plt
from matplotlib.pyplot import cm, colormaps
import seaborn as sns
import pandas as pd
import circlify
import numpy as np
import json
from matplotlib.patches import Patch
from sqlalchemy import create_engine

path = 'Clusterizzazione/'

sns.set_style('whitegrid') # Impostiamo il tema di Seaborn
sns.set_context("paper")

df = pd.read_csv(path+'FrobeniusErrorVSNComponents.csv')

plt.figure(figsize=(10,10))
ax = plt.axes()
sns.scatterplot(data=df, x='NComponents', y='FrobeniusError', legend=False, s=1000, palette='red', ax=ax)
sns.lineplot(data=df, x='NComponents', y='FrobeniusError', legend=False, linewidth=6, markers=False, style=True, dashes=[(2,2)],  palette='red', ax=ax)
plt.xticks(fontsize=25, fontweight='bold')
plt.yticks(fontsize=25, fontweight='bold')
plt.xlabel('Number of clusters', fontsize=30, fontweight='bold')
plt.ylabel('Frobenius Error', fontsize=30, fontweight='bold')
plt.savefig(path+'FrobeniusErrorVSNComponents.png', dpi=200)

