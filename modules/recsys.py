import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer
import os
import string
import pickle
from make_model.models import Shop

def get_data():
    Shop.objects.to_csv('/home/giacat/export.csv')
    print('OK')

def load_data():
    df = pd.read_csv('./data/foody_reviews.csv')
    df_business = pd.read_csv('./data/foody_items.csv')
    dict_data = {'df':df,'df_business':df_business}
    return dict_data

def get_stopwords():
    stop = []
    for word in stopwords.words('vietnamese'):
        s = [char for char in word if char not in string.punctuation]
        stop.append(''.join(s))
    return stop

def text_process(mess):
    stop = get_stopwords()
    # Check characters to see if they are in punctuation
    nopunc = [char for char in mess if char not in string.punctuation]
    # Join the characters again to form the string.
    nopunc = ''.join(nopunc)
    # Now just remove any stopwords
    return " ".join([word for word in nopunc.split() if word.lower() not in stop])

def get_yelp_data():
    data =  load_data()       
    df = data['df']
    yelp_data = df[['id', 'user', 'scores', 'content']]
    return yelp_data

def get_clean_text_yelp_data():
    print('Process cleaned text')
    yelp_data = get_yelp_data()
    yelp_data = yelp_data[yelp_data['content'].notnull()].copy()
    yelp_data['content'] = yelp_data['content'].apply(text_process)
    return yelp_data


def get_trainning_data():
    yelp_data = get_clean_text_yelp_data()
    userid_df = yelp_data[['user', 'content']]
    business_df = yelp_data[['id', 'content']]

    userid_df = userid_df.groupby('user').agg({'content': ' '.join})
    business_df = business_df.groupby('id').agg({'content': ' '.join})

    pickle.dump(userid_df,open('./data/userid_df.pkl','wb'))
    pickle.dump(business_df,open('./data/business_df.pkl','wb'))
    print('Trainning data dump')

def load_trainning_data():
    userid_df = pickle.load(open('./data/userid_df.pkl','rb'))
    business_df = pickle.load(open('./data/business_df.pkl','rb'))
    dict_trainning_data = {'userid_df':userid_df,'business_df':business_df}
    return dict_trainning_data

def get_vectorizer():
    data = load_trainning_data()
    userid_df = data['userid_df']
    business_df = data['business_df']
    # userid vectorizer
    userid_vectorizer = TfidfVectorizer(
        tokenizer=WordPunctTokenizer().tokenize, max_features=5000)
    userid_vectors = userid_vectorizer.fit_transform(userid_df['content'])

    # Business id vectorizer
    businessid_vectorizer = TfidfVectorizer(
        tokenizer=WordPunctTokenizer().tokenize, max_features=5000)
    businessid_vectors = businessid_vectorizer.fit_transform(
        business_df['content'])
    dict_vectors = {'userid_vectorizer':userid_vectorizer,'businessid_vectorizer':businessid_vectorizer,'userid_vectors':userid_vectors,'businessid_vectors':businessid_vectors}
    return dict_vectors

def get_rating_matrix():
    yelp_data = get_yelp_data()
    userid_rating_matrix = pd.pivot_table(
        yelp_data, values='scores', index=['user'], columns=['id'])
    return userid_rating_matrix

def prepare_pq():
    data_vec = get_vectorizer()
    userid_vectors = data_vec['userid_vectors']
    userid_vectorizer=data_vec['userid_vectorizer']
    businessid_vectors=data_vec['businessid_vectors']
    businessid_vectorizer=data_vec['businessid_vectorizer']
    data_df = load_trainning_data()
    userid_df = data_df['userid_df']
    business_df = data_df['business_df']
    P = pd.DataFrame(userid_vectors.toarray(), index=userid_df.index,
                    columns=userid_vectorizer.get_feature_names())
    Q = pd.DataFrame(businessid_vectors.toarray(), index=business_df.index,
                    columns=businessid_vectorizer.get_feature_names())
    dict_pq = {'P':P,'Q':Q}
    return dict_pq

def matrix_factorization(R, P, Q, steps=25, gamma=0.001, lamda=0.02):
    for step in range(steps):
        for i in R.index:
            for j in R.columns:
                if R.loc[i, j] > 0:
                    eij = R.loc[i, j] - np.dot(P.loc[i], Q.loc[j])
                    P.loc[i] = P.loc[i] + gamma * \
                        (eij * Q.loc[j] - lamda * P.loc[i])
                    Q.loc[j] = Q.loc[j] + gamma * \
                        (eij * P.loc[i] - lamda * Q.loc[j])
        e = 0
        for i in R.index:
            for j in R.columns:
                if R.loc[i, j] > 0:
                    e = e + pow(R.loc[i, j] - np.dot(P.loc[i], Q.loc[j]), 2) + lamda * (
                        pow(np.linalg.norm(P.loc[i]), 2) + pow(np.linalg.norm(Q.loc[j]), 2))
        if e < 0.001:
            break

    return P, Q

def train_PQ():
    print('START TRAINNING')
    userid_rating_matrix = get_rating_matrix()
    data = prepare_pq()
    P = data['P']
    Q = data['Q']
    P, Q = matrix_factorization(userid_rating_matrix, P, Q, steps=25, gamma=0.001,lamda=0.02)
    pickle.dump(P,open('/.data/foody_p.pkl','wb'))
    pickle.dump(Q,open('/.data/foody_q.pkl','wb'))
    print('FINISH TRAINNING')

def load_PQ():
    P = pickle.load(open('./data/tfP.pkl', 'rb'))
    Q = pickle.load(open('./data/tfQ.pkl', 'rb'))
    dict_pq = {'P':P,'Q':Q}
    return dict_pq

def recommendations(string):
    vector = get_vectorizer()
    userid_vectorizer = vector['userid_vectorizer']
    data_pq = load_PQ()
    Q=data_pq['Q']
    data = load_data()
    df_business= data['df_business']
    # words = "tôi muốn ăn tối với nhà hàng hải sản"
    test_df = pd.DataFrame([string], columns=['content'])
    test_df['content'] = test_df['content'].apply(text_process)
    test_vectors = userid_vectorizer.transform(test_df['content'])
    test_v_df = pd.DataFrame(test_vectors.toarray(
    ), index=test_df.index, columns=userid_vectorizer.get_feature_names())
    predictItemRating = pd.DataFrame(
        np.dot(test_v_df.loc[0], Q.T), index=Q.index, columns=['Rating'])
    topRecommendations = pd.DataFrame.sort_values(
        predictItemRating, ['Rating'], ascending=[0])[:7]
    for i in topRecommendations.index:
        print('index', i)
        print(df_business[df_business['id'] == i]['name'].iloc[0])
    #     print(df_business[df_business['id'] == i]['category'].iloc[0])
    #     print(str(df_business[df_business['id'] == i]['avgscore'].iloc[0]))
    #     print('')
    return topRecommendations.index


