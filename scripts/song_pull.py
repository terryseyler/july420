#!/usr/bin/env python
# coding: utf-8

# In[36]:


import requests
import json
from datetime import datetime
from sqlite3 import Error
import sqlite3
import time

song_url="https://us.api.iheart.com/api/v3/live-meta/stream/2033/currentTrackMeta?defaultMetadata=true"


# In[37]:


def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        file ="/home/terrysey/july420/DB/july420.db"
        conn = sqlite3.connect(file
        ,detect_types=sqlite3.PARSE_DECLTYPES)
        #conn.row_factory=sqlite3.Row
      
        return conn

    except Error as e:
        print("could not open pythonanywhere db".format(e))
        try:
            file="/Users/terryseyler/Library/CloudStorage/OneDrive-Personal/git/july420/DB/july420.db"
            conn = sqlite3.connect(file
            ,detect_types=sqlite3.PARSE_DECLTYPES)
            #conn.row_factory=sqlite3.Row
           
            return conn
        except Error as e:
            print("could not open local db".format(e))


# In[38]:


#pull iheart api
def pull_songs():
    try:
        r = requests.get(song_url, headers={'Cache-Control': 'no-cache'})
    except:
        "could not connect to api"
        return
    #load json
    if len(r.text)>0:
        try:
            j = json.loads(r.text)

            #parse json
            song = j['title']
            band=j['artist']
            album = j['album']
            date_time= datetime.fromtimestamp(j['startTime']/1000).strftime("%Y-%m-%d %H:%M:%S")
            print("{0} {1} {2} {3}".format(song,band,album,date_time))
            #insert into db
        except:
            print("could not parse json")
            return

        conn=create_connection()
        try:
            conn.execute(
                  'INSERT OR IGNORE INTO july2022 (song,band,album,datetime,like)'
                  ' VALUES (?, ?, ?, ?,?)',
                   (song,band,album,date_time,0)
                        )
            conn.execute("update july2022 set last_updated ='{}'".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")))
            conn.commit()
            conn.close()
        except:
            print("could not update db")
            return
    else:
        print("requests is blank")
        return


# In[40]:


while True:
    pull_songs()
    time.sleep(60)

