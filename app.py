from flask import *
from flask import Flask, request,render_template, flash, redirect, url_for, session
from wtforms import Form,StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import csv
import pyrebase
import os
import sys
import random, json
import pprint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet

movie_name=["Empty"]
MN=""

import warnings; warnings.simplefilter('ignore')


md = pd. read_csv('movies_metadata.csv')




def get_similiar_urls(title):
    
    movieName=''
    urls=[]
    new_file = pd.read_csv('URLMerge.csv')

    for index,row in new_file.iterrows():
        if row[1]==title[0]:
            movieName=row[1]
            print("movie is ",row[3])
            break

    for index,row in new_file.iterrows():
        if row[2]==movieName:
            urls.append(row[3])
    return urls

def get_similiar(title):
    genre=''
    movies,urlIDs=[],[]
    new_file = pd.read_csv('URLMerge.csv')
    
    similar_tos = new_file[new_file.Similar_To == title[0]]
    movies = list(similar_tos.Movie_Name)
    urls = list(similar_tos.getURLs)

    # for index,row in new_file.iterrows():
    #     if row[1]==title[0]:
    #         genre=row[1]
    #         break
    # for index,row in new_file.iterrows():
    #     if row[2]==genre:
    #         movies.append(row[2])
    #         url = list(new_file[new_file.Movie_Name == row[2]].getURLs)[0]
    #         print(row[2], url)
    #         urlIDs.append(url)
    #         print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            
    # print("genre uis ",genre)
    # print("Title is ",title)
    return movies, urls

def get_similiarNonPersonal(title):
    movies,genre=[],[]
    ratings=[]
    new_file = pd.read_csv('NonPersonalFilteringResultsMovies.csv')
    
    #genre= new_file[new_file.For_Genre == title[0]]
    for index,row in new_file.iterrows():
        if row[4]==title[0]:
            genre.append(row[4])
            movies.append(row[1])
            ratings.append(row[3])
    
    return movies, ratings, genre
		


def get_recommendations(title):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:31]
    movie_indices = [i[0] for i in sim_scores]
    return titles.iloc[movie_indices]
mylist = []

for chunk in  pd.read_csv('credits.csv', chunksize=20000):
    mylist.append(chunk)
credits = pd.concat(mylist, axis= 0)
del mylist

def get_director(x):
    for i in x:
        if i['job'] == 'Director':
            return i['name']
    return np.nan



config = {
    "apiKey": "AIzaSyAqiCRf2rKtl_VJUb2oJu2hUAvdRlzEMIE",
    "authDomain": "whatnow-652ee.firebaseapp.com",
    "projectId": "whatnow-652ee",
    "databaseURL": "https://whatnow-652ee-default-rtdb.firebaseio.com",
    "storageBucket": "whatnow-652ee.appspot.com",
    "messagingSenderId": "932195433967",
    "appId": "1:932195433967:web:d8ac1057552fcfe07a8a1a",
    "measurementId": "G-98GJF57TEH"
}

firebase=pyrebase.initialize_app(config)
auth=firebase.auth()
db=firebase.database()

app = Flask(__name__)







#user = auth.create_user_with_email_and_password(email,password)

@app.route('/',methods=['GET', 'POST'])
def index():
	return render_template('index.html')

@app.route('/mainpage')
def index1():
    temp,img = csv_dict_list('URLMerger.csv')
    for row in temp:
        print(row)
        #print(img)
    print(len(temp))
    return render_template('movies.html',temp=temp, img=img)

def csv_dict_list(variables_file):
    dict_list=[]
    img=[]
    ifile  = open(variables_file, encoding="utf8")
    read = csv.reader(ifile)
    counter=1
    for row in read :
        dict_list.append(row[1])

        img.append(row[3])
        if counter==900:
            break
        counter+=1
        # print(row[8])
    return dict_list, img

@app.route('/Colabrative')
def Colabrative():
    movies,index = csv_dict_listCollaborative('CollaborativeFilteringResultsMovies.csv')
    for row in movies:
        print(row)
        #print(img)
    print(len(movies))
    return render_template('moviesCollaborative.html',movies=movies, index=index)

@app.route('/BooksColabrative')
def BooksColabrative():
    movies,index = csv_dict_listCollaborative('CollaborativeFilteringResultsBooks.csv')
    for row in movies:
        print(row)
        #print(img)
    print(len(movies))
    return render_template('moviesCollaborative.html',movies=movies, index=index)

@app.route('/TvColabrative')
def TvColabrative():
    movies,index = csv_dict_listCollaborative('CollaborativeFilteringResultsTvShows.csv')
    for row in movies:
        print(row)
        #print(img)
    print(len(movies))
    return render_template('moviesCollaborative.html',movies=movies, index=index)

def csv_dict_listCollaborative(variables_file):
    dict_list=[]
    index=[]
    ifile  = open(variables_file, encoding="utf8")
    read = csv.reader(ifile)
    counter=1
    for row in read :
        dict_list.append(row[0])

        index.append(row[1])
        if counter==900:
            break
        counter+=1
        # print(row[8])
    return dict_list, index


@app.route('/NonPersonal')
def NonPersonal():
    temp,rating,genre = csv_dict_listNonPersonal('NonPersonalFilteringResultsMovies.csv')
    for row in temp:
        row=row
        genre=set(genre)
    print(genre)
    return render_template('moviesNonPersonal.html',temp=temp, rating=rating, genre=genre)

def csv_dict_listNonPersonal(variables_file):
    dict_list=[]
    genre=[]
    rating=[]
    ifile  = open(variables_file, encoding="utf8")
    read = csv.reader(ifile)
    counter=1
    for row in read :
        dict_list.append(row[1])
        rating.append(row[3])
        genre.append(row[4])
        if counter==900:
            break
        counter+=1
        # print(row[8])
    return dict_list, rating, genre


@app.route('/BooksNonPersonal')
def BooksNonPersonal():
    title,rating,scores = csv_dict_listNonPersonal('NonPersonalFilteringResultsBooks.csv')
    for row in title:
        row=row
        #genre=set(genre)
    return render_template('booksNonPersonal.html',title=title, rating=rating, scores=scores,length=len(title))

@app.route('/TvNonPersonal')
def TvNonPersonal():
    title,rating,scores = csv_dict_listNonPersonal('NonPersonalFilteringResultsTvShows.csv')
    for row in title:
        row=row
        #genre=set(genre)
    return render_template('booksNonPersonal.html',title=title, rating=rating, scores=scores,length=len(title))


def csv_dict_listNonPersonal(variables_file):
    title=[]
    rating=[]
    scores=[]
    ifile  = open(variables_file, encoding="utf8")
    read = csv.reader(ifile)
    counter=1
    for row in read :
        title.append(row[1])
        rating.append(row[2])
        scores.append(row[4])
        if counter==900:
            break
        counter+=1
        # print(row[8])
    return title, rating, scores

@app.route('/Login',methods=['GET','POST'])
def Login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['pass']
        user=auth.sign_in_with_email_and_password(email,password)
        return 'Login was Successful'
    return render_template('Login.html')


@app.route('/Signup',methods=['GET','POST'])
def Signup():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['pass']
        new_user=auth.create_user_with_email_and_password(email,password)
        return 'Signup Done'
    return render_template('Signup.html')








@app.route('/About')
def About():
    return render_template('about.html')

@app.route('/Contact')
def Contact():
    return render_template('contac.html')


#this recieves data regarding opponent name
@app.route('/receiver_name', methods = ['POST'])
def worker_name():
    file_name=request.form['name']
    print(file_name,"  ========================")
    MN=file_name
    file1 = open("movie_temp.txt","w") 
    file1.write(MN) 
    file1.close() #to change file access modes 
    return "ok"


@app.route('/results')
def Results():
    file1 = open("movie_temp.txt","r") 
    response=file1.readlines()
    print (file1.readlines())
    file1.close() 
    print(response,"---------------------")
    movies,url=get_similiar(response)
    return render_template('res.html', movies=movies, url=url, length=len(movies))

@app.route('/resultsNonPersonal')
def ResultsNonPer():
    file1 = open("movie_temp.txt","r") 
    response=file1.readlines()
    print (file1.readlines())
    file1.close() 
    print(response,"---------------------")
    movies,rating, genre=get_similiarNonPersonal(response)
    return render_template('resNonPersonal.html', movies=movies, rating=rating, length=len(movies))

def SignUpFirebase(auth,email,password):
        user=auth.create_user_with_email_and_password(email,password) 
        return auth.get_account_info(user['idToken'])
 
def SignInFirebase(auth,email,password):
        try:
                user=auth.sign_in_with_email_and_password(email,password) 
                auth.get_account_info(user['idToken'])                
                return auth.current_user['localId']
        except:
                return "null"
def CreateDatabase(auth,db,Name,email,password):
        db.child("Users").push({"Name":Name,"User_id":random.randint(0,999)})
        db.child("Users").child("User").update({"Name":Name,"User_id":random.randint(0,999)})
        SignUp(auth,email,password)
        return 1
def RetrieveData(auth,db):
        users=db.child("Users").child("User").child("Name").get().val()
        return users

if __name__ == '__main__':
    app.run(debug=True)