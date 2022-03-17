import string
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm, colormaps
import seaborn as sns
import pandas as pd
import circlify
import numpy as np
import json
from matplotlib.patches import Patch
from sqlalchemy import create_engine

from PGsDictionary import *

# Specifichiamo il numero di cluster
n_clusters = 50

path = 'Clusterizzazione/n_clusters_'+str(n_clusters)+'/'

engine = create_engine('mysql+mysqlconnector://root:Fiorentino68*@127.0.0.1:3306/VotingBehavior')

df_atti = pd.read_sql('''
SELECT IdDdl, IdParlamentareProponente
FROM Atto;
''', con=engine)

df = pd.read_csv(path+'AttiLabelProposingParty.csv')

############################
# Distribution of the topics

df = df[['Label', 'IdDdl']]
df = df.groupby('Label').size().reset_index(name='Count')
df = df.sort_values('Count', ascending=False)
#df = df.head(40)
plt.figure(figsize=(10,10))
sns.barplot(x='Count', y='Label', data=df, palette=sns.color_palette('dark'))
plt.yticks(fontsize=12)
plt.ylabel('')
plt.xlabel('Bills count per topic')
plt.tight_layout()
plt.savefig(path+'TopicsDistribution.png', dpi=200)

################################################
# Distribution of each topic with respect to PGs

df = pd.read_csv(path+'AttiLabelProposingParty.csv')
plt.figure(figsize=(50,50))
df = df.groupby(['Label', 'IdGruppo'])['IdDdl'].count().unstack()
df['Sum'] = df.sum(axis=1)
df = df.sort_values('Sum', ascending=True)
# sns.set()
# sns.set_style('white')
# sns.despine()
ax = df.iloc[:, :-1].plot(kind='barh', stacked=True, color=color_mapping_by_id)
patches = [Patch(color=v, label=k) for k, v in color_mapping_by_id.items()]
plt.yticks(fontsize=8)
plt.ylabel('')
plt.xlabel('Bills count per topic')
plt.legend(title='', labels=sigle.values(), handles=patches, frameon=False, borderpad=0.5, loc='lower right', fontsize=8)
plt.title('Bills\' Proposal Composition')
plt.tight_layout()
plt.savefig(path+'TopicCompositionProposingParty.png', dpi=200)


###########################################################
# Distribution of each topic with respect to PGs NORMALIZED

df = pd.read_csv(path+'AttiLabelProposingParty.csv')
plt.figure(figsize=(50,50))
df = df.groupby(['Label', 'IdGruppo'])['IdDdl'].count().unstack()
df['Sum'] = df.sum(axis=1)
df = df.sort_values('Sum', ascending=True)
df = df.fillna(0)
for c in df.columns[:-1]:
    df[c] = df[c]/parliament_composition[c]
df['Sum'] = 0.
df['Sum'] = df.sum(axis=1)
for row in df.index:
    for c in df.columns[:-1]:
        df.loc[row,c] = df.loc[row,c]/df.loc[row,'Sum']
#df['Sum'] = df['Sum']/sum(parliament_composition.values())
# sns.set()
# sns.set_style('white')
# sns.despine()
ax = df.iloc[:, :-1].plot(kind='barh', stacked=True, color=color_mapping_by_id)
patches = [Patch(color=v, label=k) for k, v in color_mapping_by_id.items()]
for row in df.index:
    plt.pie(data=df.loc[row,0:12])
    plt.title(row)
    plt.savefig(path+'Topic_'+string(row)+'_CompositionProposingParty_NORMALIZED.png', dpi=200)
plt.yticks(fontsize=8)
plt.ylabel('')
plt.xlabel('Bills count per topic')
ax.get_legend().remove()
#plt.legend(title='', labels=sigle.values(), handles=patches, frameon=False, borderpad=0.5, loc='lower right', fontsize=8)
plt.title('Bills\' Proposal Composition (Normalized)', fontsize=10)
plt.tight_layout()
plt.savefig(path+'TopicCompositionProposingParty_NORMALIZED.png', dpi=200)