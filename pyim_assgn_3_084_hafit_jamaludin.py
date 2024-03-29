# -*- coding: utf-8 -*-
"""PYIM_Assgn_3_084_Hafit Jamaludin.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19kyFyYHnsYjrVGvNA4PNjsgdo45I06i7

# Sentiment Analysis
## Projects Concepts
### Approaching a Project

Mengembangkan aplikasi dalam skala besar tidaklah mudah. Jangan langsung terjun dan mencoba untuk menyelesaikan semuanya sekaligus. Seperti petuah bijak berikut:

"A goal without a plan is just a wish."

Mulailah dengan rencana! Berikut beberapa langkah yang sebaiknya diikuti ketika mengembangkan aplikasi:

- buatlah outline langkah demi langkah yang dibutuhkan untuk membangun aplikasi
- kemudian tulis pseudocode
- kembangkan sintaks satu per satu

Dan sebelum submit, pastikan:

- semua bugs sudah dibasmi
- cek rubrik dan pastikan proyek kamu sudah memenuhi semua requirements

### Project Overview

DATA COLUMNS:
marketplace       - 2 letter country code of the marketplace where the review was written.
customer_id       - Random identifier that can be used to aggregate reviews written by a single author.
review_id         - The unique ID of the review.
product_id        - The unique Product ID the review pertains to. In the multilingual dataset the reviews
for the same product in different countries can be grouped by the same product_id.
product_parent    - Random identifier that can be used to aggregate reviews for the same product.
product_title     - Title of the product.
product_category  - Broad product category that can be used to group reviews
(also used to group the dataset into coherent parts).
star_rating       - The 1-5 star rating of the review.
helpful_votes     - Number of helpful votes.
total_votes       - Number of total votes the review received.
vine              - Review was written as part of the Vine program.
verified_purchase - The review is on a verified purchase.
review_headline   - The title of the review.
review_body       - The review text.
review_date       - The date the review was written.

DATA FORMAT
Tab ('\t') separated text file, without quote or escape characters.
First line in each file is header; 1 line corresponds to 1 record.

In this assignment, you have to demonstrate:

- How to load and prepare text for modeling.
- How to develop a RNN for text classification sentiment analysis with Tensorflow and improve model performance.
"""

!pip install tensorflow-datasets
!pip install tensorflow
import numpy as np
import tensorflow_datasets as tfds

tfds.disable_progress_bar()

"""## Setup
## Importing Libraries
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import csv
# %matplotlib inline

data = pd.read_csv ('https://s3.amazonaws.com/amazon-reviews-pds/tsv/amazon_reviews_us_Apparel_v1_00.tsv.gz',
                    sep='\t',
                    error_bad_lines=False)

data.shape

data.info()

numerical_columns = list(data.select_dtypes(include=['int64']).columns.values) + list(data.select_dtypes(include=['float64']).columns.values)
categorical_columns = list(data.select_dtypes(include=['object']))

# cetak variabel yang numerik
numerical_columns

# cetak variabel yang kategorikal
categorical_columns

data.head()

"""## Deskriptif Statistik untuk atribut numerikal"""

# deskriptif statistik untuk data latih
data[numerical_columns].describe()

"""## Mengetahui jumlah data untuk masing-masing katagori"""

data.groupby('verified_purchase').count()

data.groupby('product_category').count()

"""# Cleansing Data

### Memastikan tidak ada missing values pada Kolom Kategorikal
--------------------------------------------
Pada keterangan dataset yang dilampirkan, missing values pada data ditandai dengan label "unknown" pada beberapa kolom dengan tipe kategorikal. Oleh karena, kolom kategorikal yang memuat label "unknown" akan diganti menjadi nan untuk menandai adanya missing values (unstandard missing values)
"""

# Mencetak semua nilai unik pada masing-masing kolom kategori
for cat_col in categorical_columns:
    print("Nilai unik untuk kolom ", cat_col.upper())
    print(data[cat_col].unique())
    print('='*30)

# mengganti nilai uniq pada PRODUCT_CATEGORY
data['product_category'].replace('2011-08-04','Apparel',inplace=True)

"""## Merangkum total missing values (nan) values"""

# missing values pada data train
print("Jumlah nan missing values atribut kategori = ",data[categorical_columns].isnull().sum().sum())
print("Jumlah nan missing values atribut numerikal = ",data[numerical_columns].isnull().sum().sum())

"""## Penanganan Missing Values
Untuk data kategorikal, missing values akan diisi dengan modus dari atribut X, sedangkan untuk data numerikal missing values akan diisi dengan median dari atribut Z.

### Pisahkan data yang bertipe kategorik dan numerik
"""

#categorical data
data_categorical = data[categorical_columns]

# numerical data
data_numerical = data[numerical_columns]

"""### Input untuk filling nan pada atribut kategorikal"""

# Machine learning process
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, KFold
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn import metrics


# features analysis libraries
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import chi2,mutual_info_classif
from sklearn.decomposition import PCA

"""## Fit data training """

imputer_categorical = SimpleImputer(missing_values=np.nan, strategy='most_frequent')
imputer_numerical = SimpleImputer(missing_values=np.nan, strategy='most_frequent')

#Categorical
# fit dengan data training
imputer_categorical.fit(data_categorical)

#numerical
# fit dengan data training
imputer_numerical.fit(data_numerical)

# transform ke data latih
data_categorical = imputer_categorical.transform(data_categorical)
data_numerical = imputer_numerical.transform(data_numerical)

# buat hasil array ke dalam dataframe
data_categorical = pd.DataFrame(data_categorical,columns=categorical_columns)
data_numerical = pd.DataFrame (data_numerical,columns=numerical_columns)

# Concate categorical columns dengan numerical columns
data = pd.concat([data_categorical,data_numerical],axis=1)

#Check kalau masih ada missing values terlewat
# missing values pada data train
print("Jumlah nan missing values atribut kategori = ",data[categorical_columns].isnull().sum().sum())
print("Jumlah nan missing values atribut numerikal = ",data[numerical_columns].isnull().sum().sum())

data.head()

"""## Eksplorasi Data (Visualisasi
### Berapa persentase setiap nilai pada kepuasan pembelian?
"""

data['verified_purchase'].value_counts()

fig, ax = plt.subplots(1,2,figsize=(16,6))

# persentase "berlangganan deposito"
data['verified_purchase'].value_counts().plot(
    kind='pie',
    autopct='%.1f%%',
    explode=[0,0.05], 
    cmap='cool',
    shadow=True,
    ax=ax[0]
)
ax[0].set_title('Persentase Kepuasan Pembelian')
ax[0].set_ylabel('')

# Barchart besaran setiap nilai pada kelas target
data.groupby('verified_purchase').agg({'verified_purchase':'count'}).plot(
    kind='bar',
    ax=ax[1]
)
ax[1].set_title('Jumlah Kepuasan Pembelian')
ax[1].set_ylabel('Jumlah')
ax[1].set_xlabel('Kepuasan Pembelian')
ax[1].legend(title='Nilai Kepuasan')

"""## Setup 

Import matplotlib and create a helper function to plot graphs:
"""

tfds.disable_progress_bar()
import matplotlib.pyplot as plt

def plot_graphs(history, metric):
  plt.plot(history.history[metric])
  plt.plot(history.history['val_'+metric], '')
  plt.xlabel("Epochs")
  plt.ylabel(metric)
  plt.legend([metric, 'val_'+metric])

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation,TruncatedSVD
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.manifold import TSNE
from sklearn.svm import LinearSVC
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer

"""#### Menghilangkan kolom yang tidak diperlukan"""

rating = ['low','neutral','high']

def rating_y(y):
    if y<=2:
        return rating[0]
    elif y>=4:
        return rating[2]
    else:
        return rating[1]


data['rating_cat'] = data['star_rating'].apply(rating_y)

data_fix=data.drop(['marketplace', 'review_id',
                      'product_id','product_parent',
                      'product_category','helpful_votes',
                       'total_votes','vine',
                       'verified_purchase','review_headline',
                     'review_date','customer_id',
                      'product_title',], axis=1)

data_fix=data_fix.head(10000)
data_fix.head()

stemmer = SnowballStemmer("english")
tokenizer = RegexpTokenizer("[a-z']+")

def tokenize(text):
    tokens = tokenizer.tokenize(text)
    return [stemmer.stem(t) for t in tokens] 

def get_tf(data_fix, use_idf, max_df=1.0, min_df=1, ngram_range=(1,1)):
    if use_idf:
        m = TfidfVectorizer(max_df=max_df, min_df=min_df, stop_words='english', ngram_range=ngram_range, tokenizer=tokenize)
    else:
        m = CountVectorizer(max_df=max_df, min_df=min_df, stop_words='english', ngram_range=ngram_range, tokenizer=tokenize)
    
    d = m.fit_transform(data_fix.values.astype('U'))
    
    return m, d
tf_m, tf_d = get_tf(data_fix['review_body'], use_idf=False, max_df=0.90, min_df=10)
tfidf_m, tfidf_d = get_tf(data_fix['review_body'], use_idf=True, max_df=0.90, min_df=10)

n_topics = 10

def get_lda(data_fix, topics):
    m = LatentDirichletAllocation(n_components=topics, n_jobs=-1, learning_method='online').fit(data_fix)
    d = m.transform(data_fix)
    return m, d

def get_kmeans(data_fix, k, scale=True):
    if scale:
        s = MinMaxScaler()
        data = s.fit_transform(data_fix)
    
    m = KMeans(n_clusters=k).fit(data_fix)
    d = m.predict(data_fix)
    return m, d        

lda_m, lda_d = get_lda(tf_d, n_topics)
kmean_m, kmean_d = get_kmeans(tfidf_d, n_topics, scale=False)

def show_topics(model, feature_names, n_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(", ".join([feature_names[i]
                        for i in topic.argsort()[:-n_words - 1:-1]]))
    print()

def show_cluster_topics(cluster_labels, tf_matrix, feature_names, n_words):
    d = pd.DataFrame(tf_matrix.toarray())
    d['c'] = cluster_labels
    d = d.groupby('c').sum().T
    
    for col in d:
        top_n = d[col].nlargest(n_words).index.tolist()
        print("Cluster #%d:" % col)
        print(", ".join([feature_names[i]
                for i in top_n]))
    print()

print("Top 15 stemmed words per topic in LDA model\n")
show_topics(lda_m, tf_m.get_feature_names(), 15)

def get_svd(data_fix, components):
    svd = TruncatedSVD(n_components=components).fit(data_fix)
    o = pd.DataFrame(svd.transform(data_fix), columns=range(0,components))
    return svd,o

def get_tsne(data_fix, components, perplexity):
    tsne = TSNE(n_components=components, perplexity=perplexity, n_iter=1000)
    o = pd.DataFrame(tsne.fit_transform(data_fix), columns=range(0,components))
    return tsne,o

svd_v, svd_m = get_svd(tfidf_d, 50)
tnse_v, tsne_m = get_tsne(svd_m, 2, 25)

lda_c = lda_d.argmax(axis=1)

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib

def plot_scatter_2d(x, y, c, sample_size, title):
    df = pd.DataFrame({'x': x, 'y': y, 'c': c}).sample(sample_size)
    l = len(np.unique(c))
    
    ax = plt.subplot(111)
    colors = cm.rainbow(np.linspace(0, 1, l))
                                   
    for c in range(0,l):
        qq = df[df['c']==c]
        ax.scatter(qq['x'], qq['y'],c=colors[c], label=c)
    plt.legend(loc='upper left', numpoints=1, ncol=3, fontsize=8, bbox_to_anchor=(0, 0), title='Topic/Cluster')
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_title(title)
    plt.show()

get_ipython().run_line_magic('matplotlib', 'inline')
plot_scatter_2d(tsne_m[0], tsne_m[1], kmean_d, 1000, 'KMeans Clustering of Baby Products Reviews using TFIDF (t-SNE Plot)')

X_train, X_test, y_train, y_test = train_test_split(tfidf_d,
                                                    data_fix['rating_cat'],test_size=0.3)

from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
def calculate_cv(X, y):
    results = {
        'lr': [],
        'svm': [],
        'nb': [],
        'combined': []
    }
    lm = LogisticRegression()
    svm = LinearSVC()
    nb = MultinomialNB()
    vc = VotingClassifier([('lm', lm), ('svm', svm), ('nb', nb)])
    
    for c in rating:
        y_adj = np.array(y==c)
        results['lr'].append((cross_val_score(lm, X, y_adj, cv=10, scoring='accuracy').mean(), c))
        results['svm'].append((cross_val_score(svm, X, y_adj, cv=10, scoring='accuracy').mean(), c))
        results['nb'].append((cross_val_score(nb, X, y_adj, cv=10, scoring='accuracy').mean(), c))
        results['combined'].append((cross_val_score(vc, X, y_adj, cv=10, scoring='accuracy').mean(), c))
    return results

cv_scores = calculate_cv(X_test, y_test)

print("Model accuracy predictions\n")
for m,s in cv_scores.items():
    for ss in s:
        print("{M} model ({R} rating): {S:.1%}".format(M=m.upper(), R=ss[1], S=ss[0]))
    print()

def get_lr(x, y):
    models = []
    for c in rating:
        y_adj = np.array(y==c)
        lm = LogisticRegression()
        lm_f = lm.fit(x, y_adj)
        models.append(lm_f)
    return models

lr_m = get_lr(X_train, y_train)

get_ipython().run_line_magic('matplotlib', 'inline')

def plot_coef(title, model, feature_names, n_words):
    v = []
    for topic_idx, topic in enumerate(model.coef_):
        [v.append([feature_names[i], model.coef_.item(i)]) for i in topic.argsort()[:-n_words - 1:-1]]
        [v.append([feature_names[i], model.coef_.item(i)]) for i in topic.argsort()[0:n_words]]
    df = pd.DataFrame(v, columns=['Term','Coefficient']).sort_values(by='Coefficient',ascending=False)
    df['c'] = df['Coefficient']>0
    ax = df.plot(x='Term', y='Coefficient', kind='barh', color=df['c'].map({True: 'g', False: 'r'}), grid=True, legend=False,
           title=title)
    ax.set_xlabel("Coefficient")

n_terms = 12
for c in range(0,len(rating)):
    plot_coef('Top {N} words in ({R}) review model\nGreen = Associated | Red = Not Associated'.format(N=n_terms*2, R=rating[c]), 
              lr_m[c], tfidf_m.get_feature_names(), n_terms)

def test_review(text):
    test_str = [text]
    test_new = tfidf_m.transform(test_str)

    print('Review text: "{R}"\n'.format(R=test_str[0]))
    print('Model Prediction')
    for m in range(0,3):
        print('Model ({M}): {P:.1%}'.format(M=rating[m], P=lr_m[m].predict_proba(test_new)[0][1]))

"""## Coba Review Text Kepuasan Pembeli"""

test_review('I bought an apparel is reject and I returned it when it arrived.')

test_review('I really like an apparel, good looking, and the price was cheap I am glad to bought it')