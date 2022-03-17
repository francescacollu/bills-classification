import pandas as pd
from pandas.core.reshape.merge import merge
from sqlalchemy import create_engine
from datetime import date
import datetime


engine = create_engine('mysql+mysqlconnector://root:Fiorentino68*@127.0.0.1:3306/VotingBehavior')

# Specifichiamo il numero di cluster
n_clusters = 50

path = 'Clusterizzazione/n_clusters_'+str(n_clusters)

manual_labelling_df = pd.read_csv(path+'/TopicLabel.csv')

# Per ricavare il file TopicIdAttoTitolo.csv, è possibile estrarre le ultime tre colonne (Topic, IdAtto, Titolo) dalla tabella Excel Topic_Modeling_NMF
topic_modeling_nmf_df = pd.read_excel(path+'/Topic_modeling_NMF.xlsx')
topic_modeling_nmf_df = topic_modeling_nmf_df[['Topic', 'IdAtto', 'Titolo']]
topic_modeling_nmf_df.to_csv(path+'/TopicIdAttoTitolo.csv')
topic_idatto_df = pd.read_csv(path+'/TopicIdAttoTitolo.csv')

merged = manual_labelling_df.merge(topic_idatto_df, how='inner', left_on='Topic', right_on='Topic')

merged.to_csv(path+'/MacrotopicIdAtto.csv', index=False)

# Comment unless condition is fixed
######################################################################################################
# df_proposing_party = pd.read_sql('''
# SELECT DISTINCT A.*,
#                 VG.*
# FROM Atto A INNER JOIN VariazioneGruppo VG ON A.IdParlamentareProponente = VG.IdParlamentare;
# ''', con=engine)

# def GetProposingParty(df):
#     df_ddl_pproponente = pd.DataFrame()
#     lista_parlamentari = df.IdParlamentareProponente.unique()
#     lista_ddl = df.IdDdl.unique()
#     df_ddl_pproponente['IdDdl'] = pd.Series(lista_ddl)
#     df_ddl_pproponente['DataIngresso'] = pd.Series(dtype=str)
#     for i, ddl in enumerate(lista_ddl):
#         print(str(i+1) + ' over ' + str(len(lista_ddl)))
#         for parlamentare in lista_parlamentari:
#             lista_date_ingresso = list(df[(df.IdParlamentareProponente == parlamentare) & (df.IdDdl == ddl)]['DataIngresso'])
#             lista_date_ingresso.append(str(date.today()))
#             lista_date_ingresso = sorted(lista_date_ingresso, key=lambda date: datetime.datetime.strptime(date, "%Y-%m-%d"))
#             for i in range(len(lista_date_ingresso)):
                       # ! Must add the condition where the presentation happened before the enter in a party 
#                      if (lista_date_ingresso[i]) <= (df[df.IdDdl == ddl]['DataPresentazione'].iloc[0]) < (lista_date_ingresso[i+1]):
#                             df_ddl_pproponente.loc[df_ddl_pproponente.IdDdl == ddl, ['DataIngresso']] = lista_date_ingresso[i]
#     return df_ddl_pproponente

# df_atti_proposing_party = GetProposingParty(df_proposing_party)
#####################################################################################################

df_atti = pd.read_sql('''
SELECT IdDdl, IdParlamentareProponente
FROM Atto;
''', con=engine)

# df_atti_proposing_party.to_csv('Clusterizzazione/Topics/AttoWithProposingParty.csv', index=False)
df_atti_entering_party_date = pd.read_csv('Clusterizzazione/AttoWithProposingPartyEnteringDate.csv')
df_atti_entering_party_date = df_atti_entering_party_date.merge(df_atti, how='inner', on=['IdDdl'])

df_appartenenza = pd.read_sql('''
SELECT IdParlamentare AS IdParlamentareProponente,
	   DataIngresso,
       IdGruppo
FROM VariazioneGruppo;
''', con=engine)

df_atti_label_proposing_party = df_appartenenza.merge(df_atti_entering_party_date, how='inner', on=['DataIngresso', 'IdParlamentareProponente'])
macrotopic_atto = pd.read_csv(path+'/MacrotopicIdAtto.csv')
df_atti_label_proposing_party = df_atti_label_proposing_party.merge(macrotopic_atto, how='inner', left_on=['IdDdl'], right_on=['IdAtto'])
df_atti_label_proposing_party = df_atti_label_proposing_party[['IdDdl', 'Label', 'IdGruppo']]
df_atti_label_proposing_party.to_csv(path+'/AttiLabelProposingParty.csv', index=False)