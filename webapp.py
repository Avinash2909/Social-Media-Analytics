# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 00:15:05 2024

@author: sai dinesh
"""

import streamlit as st

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import plotly.express as px
import random

with open("C:/Users/hp/.spyder-py3/miniproject1/projectcss.css", "r") as f:
        css = f.read()

    # Render CSS using st.markdown
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
def get_hashtag_count(hashtag):
    url = f"https://www.instagram.com/explore/tags/{hashtag}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the element containing the count
    count_element = soup.find('meta', attrs={'property': 'og:description'})
    
    if count_element:
        count_text = count_element['content']
        count = count_text.split()[0].replace(',', '')  # Extract the count from the text
        return count
    else:
        return None

def get_count(tag):
    """
    This function takes a hashtag as an input and returns the approx. times it has been used
    on Instagram.
    """
    url = f"https://www.instagram.com/explore/tags/{tag}"
    s = requests.get(url)
    soup = BeautifulSoup(s.content, 'html.parser')
    return int(soup.find_all("meta")[6]["content"].split(" ")[0].replace("K", "000").replace("B", "000000000").replace("M", "000000").replace(".", ""))

def get_best(tag, topn):
    """
    This function takes two arguments, a hashtag and topn.
    Topn is the number of similar hashhtags you wish to find.
    This allows you to cultivate a set of 30-hashtags quickly.
    """
    url = f"https://best-hashtags.com/hashtag/{tag}/"
    s = requests.get(url)
    soup = BeautifulSoup(s.content, 'html.parser')
    tags = soup.find("div", {"class": "tag-box tag-box-v3 margin-bottom-40"}).text.split()[:topn]
    tags = [tag for tag in tags]
    return tags

def load_data():
    try:
        with open("database.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        # Handle the case where the file doesn't exist
        st.warning("Database file not found. Creating a new one.")
        data = {"hashtag_data": {}}
    except json.JSONDecodeError:
        # Handle the case where the file is empty or not valid JSON
        st.warning("Database file is empty or not in valid JSON format. Creating a new one.")
        data = {"hashtag_data": {}}
    return data
st.markdown('''<style>
[data-testid="stAppViewContainer"]{
    background-image: url('insta.jpeg');
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center;
    }
  
</style>''', unsafe_allow_html=True)

# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
# DB Management
import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()
def delete_acc(username,password):
	c.execute('DELETE FROM userstable WHERE username =? AND password = ?',(username,password))
	conn.commit()
	data=c.fetchone()
	return data


def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data



def main():
     
	st.title("HASHTAG ANALYZER")

	menu = ["Home","Login","SignUp","Delete Account"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
         image="""
        <style>
        [data-testid="stAppViewContainer"]{
            background-image: url(https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSD9KLL9KH7glY2k8qwvqFr8y-ix8HEPNeGig&usqp=CAU);
            background-size: cover;
        }
        </style>
        """
         st.markdown(image,unsafe_allow_html=True)
         
         st.subheader("Home")
         st.subheader("know the count of paticular hashtag and know related hashtags")

	elif choice == "Login":
		st.subheader("Login Section")

		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.checkbox("Login"):
			# if password == '12345':
			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username,check_hashes(password,hashed_pswd))
			if result:

				st.success("Logged In as {}".format(username))

				task = st.selectbox("Task",["hashtag count","Analytics","Profiles"])
				if task == "hashtag count":
					 
                                  num= st.number_input("Select number of tags", 1, 5)
                                  tags1=[]
                                  for i in range(num):
                                     tag = st.text_input(f"Tag {i}", key=f"tag_{i}")
                                     tags1.append(tag)
                                  count=[]
                                  for i in range(num):
                                      coun= get_hashtag_count(tags1[i])
                                      count.append(coun)
                                  if st.button("Create count"):
                                     for i in range(num):
                                         st.write(f" {tags1[i]} -- {count[i]}")
                    
                    
                    

				elif task == "Analytics":
                                   data = load_data()
                                   num_tags = st.sidebar.number_input("Select number of tags", 1, 30)
                                   st.sidebar.header("Tags")
                                   col1, col2 = st.sidebar.columns(2)

                                   tags = []
                                   sizes = []
                                   for i in range(num_tags):
                                       tag = col1.text_input(f"Tag {i}", key=f"tag_{i}")
                                       size = col2.number_input(f"Top-N {i}", 1, 10, key=f"size_{i}")
                                       tags.append(tag)
                                       sizes.append(size)

                                   # only execute if the `Create Hashtags` button is pressed
                                   if st.sidebar.button("Create Hashtags"):
                        # create a list of tab names that begin with `all`
                                       tab_names = ["all"]
                                       tab_names = tab_names + [tags[i] for i in range(num_tags)]

                        # create our Streamlit tabs
                                       tag_tabs = st.tabs(tab_names)

                        # create lists to store our data outside of our loop
                                       all_hashtags = []
                                       hashtag_data = []

                        # loop for the number of tags we have
                                       for i in range(num_tags):
                                            hashtags = get_best(tags[i], sizes[i])
                                            for hashtag in hashtags:
                                               if hashtag in data["hashtag_data"]:
                                                    hashtag_count = data["hashtag_data"][hashtag]
                                               else:
                                                    hashtag_count = get_count(hashtag.replace("#", ""))
                                                    data["hashtag_data"][hashtag] = hashtag_count
                                               hashtag_data.append((f"{hashtag}<br>{hashtag_count:,}", hashtag_count))

                                # We can use our integer, i, to populate the list of Streamlit tag objects.
                                       tag_tabs[i + 1].text_area(f"Tags for {tags[i]}", " ".join(hashtags))
                                       all_hashtags = all_hashtags + hashtags

                                       tag_tabs[0].text_area("All Hashtags", " ".join(all_hashtags))

                                       st.header("Hashtag Count Data")
                                       df = pd.DataFrame(hashtag_data, columns=["hashtag", "count"])
                                       df = df.sort_values("count")

                                       with open("database.json", "w") as f:
                                             json.dump(data, f, indent=4)
                            
                                       random_colors = ['#%06x' % random.randint(0, 0xFFFFFF) for _ in range(len(df))]


                                       fig = px.bar(df, x='hashtag',y='count', color=random_colors)
                                       st.plotly_chart(fig, use_container_width=True)
                                       
                                       st.header("PIE CHART")
                                       st.subheader("know the best trending hashtag")
                                       fig = px.pie( df,names='hashtag', values='count')
                                       st.plotly_chart(fig, use_container_width=True)
                    
				elif task == "Profiles":
					    st.subheader("User Profiles")
					    user_result = view_all_users()
					    clean_db = pd.DataFrame(user_result,columns=["Username","Password"])
					    st.dataframe(clean_db)
			else:
				st.warning("Incorrect Username/Password")





	elif choice == "SignUp":
		st.subheader("Create New Account")
		new_user = st.text_input("Username")
		new_password = st.text_input("Password",type='password')

		if st.button("Signup"):
			create_usertable()
			add_userdata(new_user,make_hashes(new_password))
			st.success("You have successfully created a valid Account")
			st.info("Go to Login Menu to login")
	elif choice == "Delete Account":

		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password')
		hashed_pswd = make_hashes(password)
		result = login_user(username,check_hashes(password,hashed_pswd))
		if st.sidebar.checkbox("Delete"):
			if result:

				result2=delete_acc(username,check_hashes(password,hashed_pswd))
				if result2:
					st.warning("username unable to delete try again")
				else:
					st.success("Account daleted successfully")
			else:
				st.warning("username not found")




if __name__ == '__main__':
	main()
