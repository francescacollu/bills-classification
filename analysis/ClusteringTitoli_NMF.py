# Clusterization of (titles of) the bills using NMF method

from os import write
from nltk.classify.decisiontree import f
import pandas as pd
import string 
from stop_words import get_stop_words
import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sqlalchemy import create_engine
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import spacy
import datetime
from datetime import date
import os

engine = create_engine('mysql+mysqlconnector://root:Fiorentino68*@127.0.0.1:3306/VotingBehavior')

# df = pd.read_sql('''
# SELECT DISTINCT IdDdl AS IdAtto,
#        Titolo
# FROM Atto;
# ''', con=engine)

df = pd.read_csv('Clusterizzazione/TitoliDdl.csv')
Documents = df['Titolo'].astype(str)

# Fissiamo il numero di cluster
n_clusters = 400

path = 'Clusterizzazione/n_clusters_'+str(n_clusters)+'/'
if not os.path.exists(path):
    os.makedirs(path)

# Definire il tokenizzatore, cioè il metodo di divisione delle stringhe in tokens ovvero sequenze di caratteri che adottiamo come forme grafiche (unità statistiche)
def mytokenizer(atto):
    tokenlist = atto.split()
    tokenlist = [token for token in tokenlist if token != """ ' """ and len(token) > 3] # escludo gli apostrofi, spesso non riconosciuti tra i caratteri di punteggiatura
    new_atto = []
    for t in tokenlist:
        if t[0:4] != "http":
            new_atto.append(t)
    new_atto = " ".join(new_atto)
    clean_atto = new_atto.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    tokens = clean_atto.split(" ")
    new_tokens = []
    for token in tokens:
        if(token.isalnum() and token.isnumeric()==False):
            new_tokens.append(token)
    return new_tokens

nlp = spacy.load('it_core_news_sm')
def mylemmatizer(atto):
    sent = []
    doc = nlp(atto)
    for word in doc:
        sent.append(word.lemma_)
    return " ".join(sent)

Documents = [mylemmatizer(doc) for doc in Documents]

# Adesso definiamo la lista delle parole che saranno escluse dalle analisi: le stop-words
stoplist_1 = get_stop_words("it")

#La uniamo a un'altra lista di un'altra libreria
stoplist_2 = stopwords.words("italian")

#Uniamo le liste e prendiamo solo i valori unici
stoplist = list(set(stoplist_1+stoplist_2))

# Vettorizzazione: è cruciale adottare il giusto metodo in base alle analisi che si vogliono produrre in seguito

# Usiamo un metodo di vettorizzazione non più basato sul mero conteggio di frequenze (TF) ma introduciamo un fattore di scala legato ai documenti. Utilizziamo quindi una vettorizzazione basata sull'indice TF-IDF (Term Frequency - Inverse Document Frequency) che misura l'importanza di un termine rispetto a un documento o a una collezione di documenti.
print('Let us begin vectorization!')
vett = TfidfVectorizer(ngram_range=(1,3),
                       max_features=1000, # n.massimo di parole da considerare
                       stop_words=stoplist+['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio',
                                           'giugno', 'luglio', 'agosto', 'dicembre', 'quartapelle', 'procopio', 'novembre',
                                           'ottobre', 'settembre', 'concernere', 'modifica', 'articolo', 'modificare', 'legge', 'testo', 'legislativo', 'disciplina', 'disposizione',
                                           'reato', 'comma', 'codice', 'norma', 'bis', 'ter', 'modificazione', 'materia', 'delega', 'disposizione', 'numero', 'misura', 'urgente', 'istituzione', 'istituire', 'decreto', 'recare', 'ratifica', 'ratificare', 'convenzione', 'governo', 'repubblica'],
                       min_df = 4, # frequenza minima di una forma grafica per essere considerata
                       tokenizer=mytokenizer)

V = vett.fit_transform(Documents) # il parametro di input deve essere una stringa
words = vett.get_feature_names_out()

print('Vectorization just finished!')

# Ora abbiamo ottenuto una matrice documenti x forme grafiche con una metrica TF*IDF e possiamo operare una riduzione dimensionale.

# Una riduzione dimensionale su una matrice testuale è un tipo di tecnica per ottenere una estrazione dei fattori latenti che caratterizzano le variabili  (= parole) del corpus.
# Utilizziamo il metodo di Non-Negative Matrix Factorization, mediante cui una matrice V può essere decomposta nel prodotto di due matrici W e H (W x H = V))

model = NMF(n_components=n_clusters, random_state=1) # occorre specificare il n. di fattori da estrarre

print('Writing Frobenius norm of the matrices difference')

# Model fit
W = model.fit_transform(V) # matrice documenti x punteggi topic
with open(path+'FrobeniusNormMatricesDifference.txt', 'w') as f:
    f.write(str(model.reconstruction_err_))
H = model.components_

# Osserviamo le saturazione delle forme grafiche sui vari topic
# Ovver: i maggiori punteggi di factor loading delle parole sui fattori estratti

word_topic_df = pd.DataFrame(H.T, index=words)

print('Wordcloud started!')
# Adesso iteriamo su ognuna delle colonne del word topic dataframe:
sns.set_style("whitegrid", {'axes.grid' : False}) # Settiamo il tema di Seaborn senza griglia
for topic in range(len(word_topic_df.columns)):
    #print("Topic " +str(topic)+ " top words\n", word_topic_df[topic].sort_values(ascending=False).head(6), "\n\n")
    wordcloud = WordCloud(background_color='black', max_words=100).generate_from_frequencies(word_topic_df[topic])
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.title('Topic '+str(topic))
    plt.savefig(path+'/Topic '+str(topic)+'.png')
    plt.close()


# Adesso esporiamo le matrici ottenute via decomposizione (W e H) in due fogli di calcolo dello stesso file Excel:
writer = pd.ExcelWriter(path+'/Topic_modeling_NMF.xlsx') # Inizializziamo il writer

document_topic_df = pd.DataFrame(W)
document_topic_df["Topic"] = document_topic_df.idxmax(axis=1) # Etichetta del topic
document_topic_df["IdAtto"] = df["IdAtto"]
document_topic_df["Titolo"] = df["Titolo"]
#document_topic_df["ProposingParty"] = df["NomeGruppoParlamentare"]

# Esportiamo i 2 dataframe
document_topic_df.to_excel(writer, sheet_name='document_topic')
word_topic_df.to_excel(writer, sheet_name='word_topic')

def GetDdlPerTopic(document_topic_df):
    df = pd.DataFrame()
    df['Topic'] = document_topic_df['Topic'].unique()
    df['DdlNumber'] = document_topic_df.groupby(['Topic']).size()
    return df

def WriteClusterFeatures(writer, word_topic_df):
    df = pd.DataFrame()
    for topic in range(len(word_topic_df.columns)):
        df[topic]= word_topic_df[topic].sort_values(ascending=False).head(50).index
    df.to_excel(writer, sheet_name='clusters_features')

WriteClusterFeatures(writer, word_topic_df)
writer.save()

df_topic_distribution = GetDdlPerTopic(document_topic_df)
df_topic_distribution = df_topic_distribution.sort_values(by=['DdlNumber'])
ax = df_topic_distribution.plot.barh(x='Topic', y='DdlNumber', rot=60, color='#822433', legend=False)
plt.tight_layout
plt.title('Bills distribution over topics')
plt.savefig(path+'/BillsDistributionOverTopics.png')

df_proposing_party = pd.read_sql('''
SELECT DISTINCT A.*,
                VG.*
FROM Atto A INNER JOIN VariazioneGruppo VG ON A.IdParlamentareProponente = VG.IdParlamentare;
''', con=engine)

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