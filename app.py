import requests
from bs4 import BeautifulSoup
from flask import Flask
import sqlite3
from sqlite3 import Error
from sqlalchemy import create_engine
import math
from jinja2 import Template
import json
from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.sampledata.iris import flowers
import pandas as pd
app= Flask(__name__)
from flask import current_app, g
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from datetime import datetime
#https://us.api.iheart.com/api/v3/live-meta/stream/2033/currentTrackMeta?defaultMetadata=true
app.config['SECRET_KEY']='bb2f7df67e28dcfbeb850ae976fdaea6'

def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        file ="/home/terrysey/july420/DB/july420.db"
        conn = sqlite3.connect(file
        ,detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory=sqlite3.Row
        engine = create_engine("sqlite:///"+file)
        return conn,engine

    except Error as e:
        print(e)
        try:
            file="DB/july420.db"
            conn = sqlite3.connect(file
            ,detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory=sqlite3.Row
            engine = create_engine("sqlite:///"+file)
            return conn,engine
        except Error as e:
            print(e)
colormap = {'setosa': 'red', 'versicolor': 'green', 'virginica': 'blue'}
colors = [colormap[x] for x in flowers['species']]

def make_agg_plot(year):
    conn,engine = create_connection()
    if year =='2022':
        agg_sql="""select count(*) as volume
                    ,band
                    from july2022
                    group by band
                    order by count(*) desc
                """
    else:
        agg_sql = """select count(*) as volume
                    ,band
                    ,year
            from july420
            where year ='{0}'
            group by band
            order by count(*) desc""".format(year)
    df = pd.read_sql(agg_sql,conn)
    p = figure(x_range=df['Band'].head(10), height=500, title="July 420 Top 10 Bands {}".format(year),toolbar_location=None, tools="")
    p.vbar(x=df['Band'].head(10), top=df['volume'].head(10), width=0.9)
    p.xaxis.major_label_orientation = math.pi/6
    return p
@app.route('/')
def index():
    conn,engine = create_connection()
    cursor=conn.cursor()

    data_2020 = cursor.execute("""select * from july420 where year = '2020'""").fetchall()

    data_2021 = cursor.execute("""select * from july420 where year = '2021'""").fetchall()

    return render_template('index.html',data_2020=data_2020,data_2021=data_2021)

@app.route("/",methods=['POST'])
def song_search():
    if request.method=='POST':
        if request.form['submit_button'] == 'Search Song':
            song=request.form['song']
            conn,engine=create_connection()
            cursor=conn.cursor()
            data_2020=cursor.execute("""select *
                                        from july420
                                        where Year = '2020'
                                        and Song like '%{0}%'
                                        """.format(song)
                                        ).fetchall()
            data_2021=cursor.execute("""select *
                                        from july420
                                        where Year = '2021'
                                        and Song like '%{0}%'
                                        """.format(song)
                                        ).fetchall()

            return render_template('index.html',data_2020=data_2020,data_2021=data_2021)

        elif request.form['submit_button'] == 'Search Band':
            band=request.form['band']
            conn,engine=create_connection()
            cursor=conn.cursor()
            data_2020=cursor.execute("""select *
                                        from july420
                                        where Year = '2020'
                                        and Band like '%{0}%'
                                        """.format(band)
                                        ).fetchall()
            data_2021=cursor.execute("""select *
                                        from july420
                                        where Year = '2021'
                                        and Band like '%{0}%'
                                        """.format(band)
                                        ).fetchall()

            return render_template('index.html',data_2020=data_2020,data_2021=data_2021)
        if request.form['submit_button'] == 'Reset':
            return redirect(url_for('index'))

@app.route('/2022')
def twentytwentytwo():
    conn,engine=create_connection()
    cursor=conn.cursor()

    #print("max date is {}".format(max_date[0][0]))
    #print("now is {}".format(datetime.now()))
    #time_obj = datetime.strptime(max_date[0][0],"%Y-%m-%d %H:%M:%S")
    #dif = datetime.now() - time_obj
    #if (dif.total_seconds()/60) > 3:
        #print("Greater than 3 minutes, pulling data")
        #pull_songs()
    #else:
        #print("data up to date")
    distinct_dates = cursor.execute("select distinct date(datetime(datetime,'-4 hours')) as distinct_date from july2022 order by datetime desc").fetchall()
    data_2022=cursor.execute("""select DateTime,time(datetime(datetime,'-4 hours')) as song_time,Song,Band,datetime(DateTime,'-4 hours') as DateTime_Fixed,date(datetime(DateTime,'-4 hours')) as DatePart,LIKE from july2022 order by DateTime desc""").fetchall()

    return render_template('2022.html',data_2022=data_2022,distinct_dates=distinct_dates)

@app.route('/2022',methods=['POST','GET'])
def add_song():
    conn,engine=create_connection()
    cursor=conn.cursor()
    if request.method=='POST':

        if request.form['submit_button'] == 'Add':
            song=request.form['songAdd']
            band=request.form['bandAdd']
            rank=request.form['rankAdd']
            print("{0} {1} {2}".format(song, band, rank))
            try:
                int(rank)
            except ValueError:
                print("rank not an int")
                return redirect(url_for('twentytwentytwo'))
            if int(rank) > 420 or int(rank) <0:
                flash("Rank must be between 1 and 420")
                print("not added")
            else:
                cursor.execute("""DELETE from july420 where rank='{}' and year='2022'""".format(rank))
                conn.commit()
                cursor.execute(
                    'INSERT INTO july420 (song,band,rank,year)'
                    ' VALUES (?, ?, ?, ?)',
                    (song,band,rank,'2022')
                )
                print("added to db")
                conn.commit()

            return redirect(url_for('twentytwentytwo'))
        elif request.form['submit_button'] == 'Reset':
            return redirect(url_for('twentytwentytwo'))
        elif request.form['submit_button'] == 'Search Song':
            song=request.form['song']
            distinct_dates = cursor.execute("""select distinct
                                            date(datetime(datetime,'-4 hours')) as distinct_date
                                            from july2022
                                            where Song like '%{0}%'
                                            order by datetime desc""".format(song)
                                            ).fetchall()
            data_2022=cursor.execute("""select DateTime
                                            ,time(datetime(datetime,'-4 hours')) as song_time
                                            ,Song
                                            ,Band
                                            ,datetime(DateTime,'-4 hours') as DateTime_Fixed
                                            ,date(datetime(DateTime,'-4 hours')) as DatePart
                                            ,LIKE
                                            from july2022
                                        where Song like '%{0}%'
                                        order by DateTime desc
                                        """.format(song)
                                        ).fetchall()

            return render_template('2022.html',data_2022=data_2022,distinct_dates=distinct_dates)

        elif request.form['submit_button'] == 'Search Band':
            band=request.form['band']
            distinct_dates = cursor.execute("""select distinct
                                date(datetime(datetime,'-4 hours')) as distinct_date
                                from july2022
                                where Band like '%{0}%'
                                order by datetime desc""".format(band)
                                ).fetchall()
            data_2022=cursor.execute("""select DateTime
                                            ,time(datetime(datetime,'-4 hours')) as song_time
                                            ,Song
                                            ,Band
                                            ,datetime(DateTime,'-4 hours') as DateTime_Fixed
                                            ,date(datetime(DateTime,'-4 hours')) as DatePart
                                            ,LIKE
                                            from july2022
                                        where Band like '%{0}%'
                                        order by DateTime desc
                                        """.format(band)
                                        ).fetchall()
            return render_template('2022.html',data_2022=data_2022,distinct_dates=distinct_dates)
    return redirect(url_for('twentytwentytwo'))

@app.route('/delete/<int:Rank>')
def delete(Rank):
    conn,engine=create_connection()
    cursor=conn.cursor()
    cursor.execute("DELETE from july420 where rank= '{}' and year ='2022'".format(Rank))
    conn.commit()
    return redirect(url_for('twentytwentytwo'))

@app.route('/like/<DateTime>',methods=('GET','POST'))
def like(DateTime):
    conn,engine=create_connection()
    cursor=conn.cursor()
    print(DateTime.replace('%',' '))
    cursor.execute("UPDATE july2022 set like = like + 1 where DateTime='{}'".format(DateTime.replace('%',' ')))
    conn.commit()
    conn.close()
    return redirect(url_for('twentytwentytwo'))

@app.route('/dislike/<DateTime>',methods=('GET','POST'))
def dislike(DateTime):
    conn,engine=create_connection()
    cursor=conn.cursor()
    print(DateTime.replace('%',' '))
    cursor.execute("UPDATE july2022 set like = like - 1 where DateTime='{}'".format(DateTime.replace('%',' ')))
    conn.commit()
    conn.close()
    return redirect(url_for('twentytwentytwo'))

@app.route('/plot')
def plot():
    return render_template('plot.html',resources=CDN.render())

@app.route('/myplot')
def myplot():
    p = make_agg_plot('2020')
    return json.dumps(json_item(p,"myplot"))

@app.route('/myplot2')
def myplot2():
    p = make_agg_plot('2021')
    return json.dumps(json_item(p,"myplot2"))

@app.route('/myplot3')
def myplot3():
    p = make_agg_plot('2022')
    return json.dumps(json_item(p,"myplot3"))

def pull_songs():
    conn,engine=create_connection()
    cursor=conn.cursor()

    r = requests.get("https://1059thex.iheart.com/music/recently-played/", headers={"Cache-Control": "no-cache","Pragma": "no-cache"})

    soup = BeautifulSoup(r.content, "html.parser")

    track= [track.text for track in soup.find_all(class_="track-title")]
    artist= [artist.text for artist in soup.find_all(class_="track-artist")]
    album= [album.text for album in soup.find_all(class_="track-album")]
    time=[time['datetime'] for time in soup.find_all(class_="component-datetime-display track-time")]

    df = pd.DataFrame([track,artist,album,time]).transpose()
    df.columns=['Song','Band','Album','DateTime']
    df['DateTime'] = pd.to_datetime(df['DateTime'])

    #df.sort_values(by='DateTime' ,inplace=True)
    cursor.execute("DELETE FROM july2022_stage")
    conn.commit()
    df.to_sql("july2022_stage",engine,if_exists='append',index=False)
    conn.commit()
    cursor.execute("INSERT OR IGNORE INTO july2022 select *,0 as LIKE,'filler' as last_updated FROM july2022_stage")
    conn.execute("update july2022 set last_updated ='{}'".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")))
    conn.commit()
    conn.close()
    r.close()
    del r
