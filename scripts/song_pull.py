#!/usr/bin/env python
# coding: utf-8

# In[36]:


import requests
import json
from datetime import datetime
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

    except:
        print("could not open pythonanywhere db")
        try:
            file="/Users/terryseyler/Library/CloudStorage/OneDrive-Personal/git/july420/DB/july420.db"
            conn = sqlite3.connect(file
            ,detect_types=sqlite3.PARSE_DECLTYPES)
            #conn.row_factory=sqlite3.Row

            return conn
        except:
            print("could not open local db")


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
            albumid = str(j['albumId'])
            artistid = str(j['artistId'])
            trackid = str(j['trackId'])
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
                  'INSERT OR IGNORE INTO july2022 (song,band,album,datetime,like,albumid,artistid,trackid)'
                  ' VALUES (?, ?, ?, ?,?,?,?,?)',
                   (song,band,album,date_time,0,albumid,artistid,trackid)
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

