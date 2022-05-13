from matplotlib import colors
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from datetime import date
import pandas as pd
import numpy as np
import seaborn as sns
from seaborn.palettes import color_palette

engine = create_engine('mysql+mysqlconnector://root:Fiorentino68*@127.0.0.1:3306/VotingBehavior')

df = pd.read_sql('''
SELECT A.*,
       VG.*
FROM Atto A INNER JOIN VariazioneGruppo VG ON A.IdParlamentareProponente = VG.IdParlamentare
WHERE IdDdl IN
('48904', 
'49151', 
'49013', 
'53457', 
'52566', 
'49514', 
'53122', 
'53168', 
'52853', 
'52937', 
'50402', 
'52862', 
'53554', 
'48654', 
'51706', 
'53417', 
'50097', 
'53576', 
'49511', 
'51499', 
'51570', 
'52535', 
'53343', 
'53239', 
'54010', 
'51564', 
'52387', 
'51595', 
'51787', 
'54184', 
'53475', 
'ac18_272', 
'ac18_375', 
'ac18_1791', 
'ac18_572', 
'ac18_1036', 
'ac18_1722', 
'ac18_1741');
''', con=engine)

color_mapping = {'MoVimento 5 Stelle': 'yellow',
'Misto':'grey',
'Forza Italia-Berlusconi Presidente':'blue',
'Coraggio Italia':'royalblue',
'Partito Democratico':'red',
'Italia Viva - P.S.I.':'deeppink',
'Fratelli d\'Italia':'black',
'Liberi e Uguali':'darkred',
'Lega-Salvini Premier-Partito Sardo d\'Azione':'green',
'Per le Autonomie (SVP-PATT, UV)':'lightsalmon',
'Europeisti-MAIE-Centro Democratico':'aquamarine'}

color_mapping_by_id = {0: 'yellow',
1:'green',
2:'blue',
3:'royalblue',
4:'red',
5:'deeppink',
6:'black',
7:'darkred',
8:'green',
9:'lightsalmon',
10:'deeppink',
11:'aquamarine',
12:'grey'}

sigle = {0: 'M5S',
1:'LEGA',
2:'FI',
3:'CI',
4:'PD',
5:'IV',
6:'FDI',
7:'LEU',
8:'LEGA-PSdAZ',
9:'AUT',
10:'IV-PSI',
11:'EURCD',
12:'MISTO'}

def GetProposingParty(df):
    df_ddl_pproponente = pd.DataFrame()
    lista_parlamentari = df.IdParlamentareProponente.unique()
    #print(lista_parlamentari)
    lista_ddl = df.IdDdl.unique()
    #print(lista_ddl)
    df_ddl_pproponente['IdDdl'] = pd.Series(lista_ddl)
    df_ddl_pproponente['DataIngresso'] = pd.Series(dtype=str)
    for ddl in lista_ddl:
        for parlamentare in lista_parlamentari:
            lista_date_ingresso = list(df[(df.IdParlamentareProponente == parlamentare) & (df.IdDdl == ddl)]['DataIngresso'])
            lista_date_ingresso.append(str(date.today()))
            lista_date_ingresso = sorted(lista_date_ingresso, key=lambda date: datetime.datetime.strptime(date, "%Y-%m-%d"))
            #print(lista_date_ingresso)
            for i in range(len(lista_date_ingresso)):
                if (lista_date_ingresso[i]) <= (df[df.IdDdl == ddl]['DataPresentazione'].iloc[0]) < (lista_date_ingresso[i+1]):
                    df_ddl_pproponente.loc[df_ddl_pproponente.IdDdl == ddl, ['DataIngresso']] = lista_date_ingresso[i]
    return df_ddl_pproponente

df_proposing_party = GetProposingParty(df)
df_proposing_party2 = df.merge(df_proposing_party, how='inner', on=['DataIngresso', 'IdDdl'])
writer = pd.ExcelWriter('Clusterizzazione/Topics/ViolenzaGenere.xlsx') # this is about Violenza di Genere topic
df_proposing_party2.to_excel(writer, sheet_name='ddl')
writer.save()

df_proposing_party2_count = pd.DataFrame({'Count' : df_proposing_party2.groupby(['IdGruppo']).size()}).reset_index()
df_proposing_party2_count = df_proposing_party2_count.sort_values(by='Count', ascending=False)
df_proposing_party2_count['Sigle'] = df_proposing_party2_count['IdGruppo'].apply(lambda x: sigle.get(x))

# Bar chart

# x_pos = np.arange(len(list(df_proposing_party2_count.index)))
# plt.bar(x=df_proposing_party2_count.IdGruppo, height=df_proposing_party2_count.Count, color=df_proposing_party2_count['IdGruppo'].map(color_mapping_by_id))
# plt.xticks(x_pos, list(df_proposing_party2_count.Sigle))
# plt.title('Proposals Distribution over Parliamentary Groups')
# plt.tight_layout()
# plt.show()


# Pie chart
df_proposing_party2_count.index = df_proposing_party2_count.Sigle
df_proposing_party2_count.plot.pie(y='Count', colors=df_proposing_party2_count['IdGruppo'].map(color_mapping_by_id), legend=False, autopct='%1.1f%%', ylabel='')
#plt.rcParams['text.color'] = 'b'
plt.title('Proposals Distribution over Parliamentary Groups about \n Gender Discrimination \n (Non-Normalized)')
plt.tight_layout()
plt.savefig('Clusterizzazione/Topics/ProposalsDistribution_GenderDiscrimination.png')