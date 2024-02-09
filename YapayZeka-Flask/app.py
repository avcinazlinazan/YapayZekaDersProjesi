from os import read
from flask import Flask, request, render_template

import pandas as pd
import numpy as np
import neattext.functions as nfx
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from dashboard import getvaluecounts, getlevelcount, getsubjectsperlevel


app = Flask(__name__)


def getcosinemat(df):

    countvect = CountVectorizer()
    cvmat = countvect.fit_transform(df['product_Info'])
    return cvmat

# getting the title which doesn't contain stopwords and all which we removed with the help of nfx


def getcleantitle(df):

    df['product_Info'] = df['productInfo'].apply(nfx.remove_stopwords)

    df['product_Info'] = df['product_Info'].apply(nfx.remove_special_characters)

    return df


def cosinesimmat(cv_mat):

    return cosine_similarity(cv_mat)


def readdata():

    df = pd.read_csv('ProductCleanedTitle.csv')
    return df

# this is the main recommendation logic for a particular title which is choosen


def recommend_product(df, product_Info, cosine_mat, numrec):

    product_index = pd.Series(
        df.index, index=df['product_Info']).drop_duplicates()

    index = product_index[product_Info]

    scores = list(enumerate(cosine_mat[index]))

    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

    selected_product_index = [i[0] for i in sorted_scores[1:]]

    selected_product_score = [i[1] for i in sorted_scores[1:]]

    rec_df = df.iloc[selected_product_index]

    rec_df['Similarity_Score'] = selected_product_score

    final_recommended_products = rec_df[[
        'productInfo', 'Similarity_Score', 'productLink', 'productPrice', 'productName']]

    return final_recommended_products.head(numrec)

# this will be called when a part of the title is used,not the complete title!


def searchterm(term, df):
    result_df = df[df['product_Info'].str.contains(term)]
    top6 = result_df.sort_values(by='productPrice', ascending=False).head(6)
    return top6


# extract features from the recommended dataframe

def extractfeatures(recdf):

    product_url = list(recdf['productLink'])
    product_title = list(recdf['productInfo'])
    product_price = list(recdf['productPrice'])

    return product_url, product_title, product_price


@app.route('/', methods=['GET', 'POST'])
def hello_world():

    if request.method == 'POST':

        my_dict = request.form
        productname = my_dict['product']
        print(productname)
        try:
            df = readdata()
            df = getcleantitle(df)
            cvmat = getcosinemat(df)

            num_rec = 6
            cosine_mat = cosinesimmat(cvmat)

            recdf = recommend_product(df, productname,
                                    cosine_mat, num_rec)

            product_url, product_title, product_price = extractfeatures(recdf)

            # print(len(extractimages(product_url[1])))

            dictmap = dict(zip(product_title, product_url))

            if len(dictmap) != 0:
                return render_template('index.html', productmap=dictmap, productname=productname, showtitle=True)

            else:
                return render_template('index.html', showerror=True, productname=productname)

        except:

            resultdf = searchterm(productname, df)
            if resultdf.shape[0] > 6:
                resultdf = resultdf.head(6)
                product_url, product_title, product_price = extractfeatures(
                    resultdf)
                productmap = dict(zip(product_title, product_url))
                if len(productmap) != 0:
                    return render_template('index.html', productmap=productmap, productname=productname, showtitle=True)

                else:
                    return render_template('index.html', showerror=True, productname=productname)

            else:
                product_url, product_title, product_price = extractfeatures(
                    resultdf)
                productmap = dict(zip(product_title, product_url))
                if len(productmap) != 0:
                    return render_template('index.html', productmap=productmap, productname=productname, showtitle=True)

                else:
                    return render_template('index.html', showerror=True, productname=productname)

    return render_template('index.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    df = readdata()
    valuecounts = getvaluecounts(df)

    levelcounts = getlevelcount(df)

    subjectsperlevel = getsubjectsperlevel(df)

    

    return render_template('dashboard.html', valuecounts=valuecounts, levelcounts=levelcounts,
                        subjectsperlevel=subjectsperlevel )


if __name__ == '__main__':
    app.run(debug=True)
