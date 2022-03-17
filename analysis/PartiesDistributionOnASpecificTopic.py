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

# Specifichiamo il tema
topic = 'PARITA_DI_GENERE'

path = 'ClassificazioneTeseo/'

engine = create_engine('mysql+mysqlconnector://root:Fiorentino68*@127.0.0.1:3306/VotingBehavior')

bills_id = pd.read_sql('''
SELECT DISTINCT IdDdl 
FROM VotingBehavior.ClassificazioneTitoli
WHERE Topic IN
('DIRITTI FONDAMENTALI TRADIZIONALI',
'EGUAGLIANZA',
'REATI CONTRO I DIRITTI FONDAMENTALI',
'REATI SESSUALI',
'VIOLENZA E MINACCE',
'VIOLENZA PSICOLOGICA E MOBBING',
"PARITA' TRA SESSI",
'RELAZIONI DI GENERE'
);
''', con=engine)

df = pd.read_csv(path+'AttiLabelProposingParty.csv')
df = df[['IdDdl', 'IdGruppo']]

df = df.merge(bills_id, how='inner', on=['IdDdl'])

df['IdGruppo'] = df['IdGruppo'].replace(sigle) # Sostituiamo l'id del gruppo con la sigla: questo sarà utile per avere la sigla identificativa nel grafico a torta

################################################
# Distribution of topic with respect to PGs

plt.figure(figsize=(20,20))
df_pie = df.groupby('IdGruppo').count().reset_index()
labels=list(df_pie.IdGruppo)
fig, ax = plt.subplots()
ax.pie(list(df_pie.IdDdl), labels=labels, textprops={'fontsize': 15, 'weight':'bold'}, wedgeprops={"linewidth": 1, "edgecolor": "white"}, colors=[color_mapping_by_sigla[key] for key in labels])

ax.set_title('PGs distribution on topic '+topic, fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig(path+'Distribution_on_topic_'+topic+'.png', dpi=200)
