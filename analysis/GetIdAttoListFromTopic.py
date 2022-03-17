from email.policy import strict
import pandas as pd
from pandas.core.reshape.merge import merge
from sqlalchemy import create_engine
from datetime import date
import datetime
import string

# Specifichiamo il numero di cluster
n_clusters = 50
topic = 27

path = 'Clusterizzazione/n_clusters_'+str(n_clusters)+'/'

topic_idatto_df = pd.read_csv(path+'/TopicIdAttoTitolo.csv')

topic_idatto_df = topic_idatto_df[topic_idatto_df['Topic'] == 27]['IdAtto']
topic_idatto_df.to_csv(path+'IdAttoList_'+str(topic)+'_.csv', index=False)


