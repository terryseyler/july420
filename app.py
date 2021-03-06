import requests
from bs4 import BeautifulSoup
from flask import Flask
import sqlite3
from sqlite3 import Error
from sqlalchemy import create_engine
import math
import json
from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.sampledata.iris import flowers
import pandas as pd
app= Flask(__name__)
from flask import (
    flash, redirect, render_template, request, url_for
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
    if year =='today':
        agg_sql="""select count(*) as volume
                    ,band
                    from july2022
                    where date(datetime(datetime,'-4 hours'))= (select max(date(datetime(datetime,'-4 hours'))) from july2022)
                    group by band
                    order by count(*) desc
                """
        title = 'Top 10 bands played for today'
    elif year =='yesterday':
        agg_sql="""select count(*) as volume
                    ,band
                    from july2022
                    where date(datetime(datetime,'-4 hours'))= (select date(max(date(datetime(datetime,'-4 hours'))),'-1 day') from july2022)
                    group by band
                    order by count(*) desc
                """
        title = 'Top 10 bands played for yesterday'
    else:
        agg_sql = """select count(*) as volume
                    ,band
                    ,year
            from july420
            where year ='{0}'
            group by band
            order by count(*) desc""".format(year)
        title = "July 420 Top 10 Bands for {}".format(year)
    df = pd.read_sql(agg_sql,conn)
    p = figure(x_range=df['Band'].head(10), height=500, title=title,toolbar_location=None, tools="")
    p.vbar(x=df['Band'].head(10), top=df['volume'].head(10), width=0.9)
    p.xaxis.major_label_orientation = math.pi/4
    return p
@app.route('/july420')
def index():
    conn,engine = create_connection()
    cursor=conn.cursor()

    data_2020 = cursor.execute("""select * from july420 where year = '2020'""").fetchall()

    data_2021 = cursor.execute("""select * from july420 where year = '2021'""").fetchall()
    data_2022 = cursor.execute("""with ranks as
                                (select upper(Song) as Song
                                ,upper(Band) as Band
                                ,datetime(datetime,'-4 hours') as datetime
                                ,421 - ROW_NUMBER() OVER (ORDER BY datetime) as Rank
                                from july2022
                                where   datetime(datetime,'-4 hours') between '2022-07-01 16:20:00' and '2022-07-01 23:59:59'
                                    or  datetime(datetime,'-4 hours') between '2022-07-02 10:00:00' and '2022-07-02 21:00:00'
                                    or  datetime(datetime,'-4 hours') between '2022-07-03 10:00:00' and '2022-07-03 21:00:00'
                                    or  datetime(datetime,'-4 hours') between '2022-07-04 10:00:00' and '2022-07-04 21:00:00'
                               order by datetime
                               limit 420
                               )
                               select * from ranks order by datetime desc
                """).fetchall()

    return render_template('index.html',data_2020=data_2020,data_2021=data_2021,data_2022=data_2022)

@app.route("/july420",methods=['POST'])
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
            data_2022 = cursor.execute("""with ranks as
                                (
                                select upper(Song) as Song
                            ,upper(Band) as Band
                            ,datetime(datetime,'-4 hours') as datetime
                            ,421 - ROW_NUMBER() OVER (ORDER BY datetime) as Rank
                            from july2022
                            where  (datetime(datetime,'-4 hours') between '2022-07-01 16:20:00' and '2022-07-01 23:59:59'
                                or  datetime(datetime,'-4 hours') between '2022-07-02 10:00:00' and '2022-07-02 21:00:00'
                                or  datetime(datetime,'-4 hours') between '2022-07-03 10:00:00' and '2022-07-03 21:00:00'
                                or  datetime(datetime,'-4 hours') between '2022-07-04 10:00:00' and '2022-07-04 21:00:00'
                                )

                           order by datetime
                           limit 420
                           )
                         select * from ranks where Song like '%{}%' order by datetime desc
                        """.format(song)
                        ).fetchall()

            return render_template('index.html',data_2020=data_2020,data_2021=data_2021,data_2022=data_2022)

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
            data_2022 = cursor.execute("""with ranks as
                                (
                                select upper(Song) as Song
                            ,upper(Band) as Band
                            ,datetime(datetime,'-4 hours') as datetime
                            ,421 - ROW_NUMBER() OVER (ORDER BY datetime) as Rank
                            from july2022
                            where  (datetime(datetime,'-4 hours') between '2022-07-01 16:20:00' and '2022-07-01 23:59:59'
                                or  datetime(datetime,'-4 hours') between '2022-07-02 10:00:00' and '2022-07-02 21:00:00'
                                or  datetime(datetime,'-4 hours') between '2022-07-03 10:00:00' and '2022-07-03 21:00:00'
                                or  datetime(datetime,'-4 hours') between '2022-07-04 10:00:00' and '2022-07-04 21:00:00'
                                )

                           order by datetime
                           limit 420
                           )
                         select * from ranks where Band like '%{}%' order by datetime desc
                        """.format(band)
                        ).fetchall()
            return render_template('index.html',data_2020=data_2020,data_2021=data_2021,data_2022=data_2022)
        if request.form['submit_button'] == 'Reset':
            return redirect(url_for('index'))

@app.route('/')
def twentytwentytwo():
    conn,engine=create_connection()
    cursor=conn.cursor()
    distinct_dates = cursor.execute("select distinct date(datetime(datetime,'-4 hours')) as distinct_date from july2022  where date(datetime(july2022.DateTime,'-4 hours')) >= date(datetime('now','-4 hours'),'-1 days') order by datetime desc").fetchall()
    data_2022=cursor.execute("""with ranks as
                                (select upper(Song) as Song
                                ,upper(Band) as Band
                                ,datetime
                                ,trackid
                                ,421 - ROW_NUMBER() OVER (ORDER BY datetime) as Rank
                                from july2022
                                where   datetime(datetime,'-4 hours') between '2022-07-01 16:20:00' and '2022-07-01 23:59:59'
                                    or  datetime(datetime,'-4 hours') between '2022-07-02 10:00:00' and '2022-07-02 21:00:00'
                                    or  datetime(datetime,'-4 hours') between '2022-07-03 10:00:00' and '2022-07-03 21:00:00'
                                    or  datetime(datetime,'-4 hours') between '2022-07-04 10:00:00' and '2022-07-04 21:00:00'
                               order by datetime
                               limit 420
                               )
                    select july2022.DateTime
                                    ,time(datetime(july2022.datetime,'-4 hours')) as song_time
                                    ,july2022.Song
                                    ,july2022.Band
                                    ,july2022.trackid
                                    ,july2022.artistid
                                    ,datetime(july2022.DateTime,'-4 hours') as DateTime_Fixed
                                    ,date(datetime(july2022.DateTime,'-4 hours')) as DatePart
                                    ,july2022.LIKE
                                    ,ranks.Rank
                    from july2022
                    left join ranks
                    on ranks.datetime=july2022.datetime
                    where date(datetime(july2022.DateTime,'-4 hours')) >= date(datetime('now','-4 hours'),'-1 days')
                                order by july2022.DateTime desc
                                """).fetchall()

    return render_template('2022.html',data_2022=data_2022,distinct_dates=distinct_dates)

@app.route('/',methods=['POST','GET'])
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
            data_2022=cursor.execute("""with ranks as
                                        (select upper(Song) as Song
                                        ,upper(Band) as Band
                                        ,datetime
                                        ,421 - ROW_NUMBER() OVER (ORDER BY datetime) as Rank
                                        from july2022
                                        where   datetime(datetime,'-4 hours') between '2022-07-01 16:20:00' and '2022-07-01 23:59:59'
                                            or  datetime(datetime,'-4 hours') between '2022-07-02 10:00:00' and '2022-07-02 21:00:00'
                                            or  datetime(datetime,'-4 hours') between '2022-07-03 10:00:00' and '2022-07-03 21:00:00'
                                            or  datetime(datetime,'-4 hours') between '2022-07-04 10:00:00' and '2022-07-04 21:00:00'
                                       order by datetime
                                       limit 420
                                       )
                            select july2022.DateTime
                                            ,time(datetime(july2022.datetime,'-4 hours')) as song_time
                                            ,july2022.Song
                                                ,july2022.trackid
                                            ,july2022.Band
                                            ,datetime(july2022.DateTime,'-4 hours') as DateTime_Fixed
                                            ,date(datetime(july2022.DateTime,'-4 hours')) as DatePart
                                            ,july2022.LIKE
                                            ,july2022.artistid
                                            ,ranks.Rank
                            from july2022
                            left join ranks
                            on ranks.datetime=july2022.datetime
                            where july2022.song like '%{0}%'
                                        order by july2022.DateTime desc
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
            data_2022=cursor.execute("""with ranks as
                                        (select upper(Song) as Song
                                        ,upper(Band) as Band
                                        ,datetime
                                        ,421 - ROW_NUMBER() OVER (ORDER BY datetime) as Rank
                                        from july2022
                                          where datetime(datetime,'-4 hours') between '2022-07-01 16:20:00' and '2022-07-01 23:59:59'
                                            or  datetime(datetime,'-4 hours') between '2022-07-02 10:00:00' and '2022-07-02 21:00:00'
                                            or  datetime(datetime,'-4 hours') between '2022-07-03 10:00:00' and '2022-07-03 21:00:00'
                                            or  datetime(datetime,'-4 hours') between '2022-07-04 10:00:00' and '2022-07-04 21:00:00'
                                       order by datetime
                                       limit 420
                                       )
                            select july2022.DateTime
                                            ,time(datetime(july2022.datetime,'-4 hours')) as song_time
                                            ,july2022.Song
                                            ,july2022.Band
                                            ,datetime(july2022.DateTime,'-4 hours') as DateTime_Fixed
                                            ,date(datetime(july2022.DateTime,'-4 hours')) as DatePart
                                            ,july2022.LIKE
                                                ,july2022.trackid
                                                ,july2022.artistid
                                            ,ranks.Rank
                            from july2022
                            left join ranks
                            on ranks.datetime=july2022.datetime
                            where july2022.band like '%{0}%'
                                        order by july2022.DateTime desc
                                        """.format(band)
                                        ).fetchall()
            return render_template('2022.html',data_2022=data_2022,distinct_dates=distinct_dates)
        elif request.form['submit_button'] == 'July 420 Filter':
            conn,engine=create_connection()
            cursor=conn.cursor()
            distinct_dates = cursor.execute("""select distinct date(datetime(datetime,'-4 hours')) as distinct_date
                                                    from  july2022
                                                     where datetime(datetime,'-4 hours') between '2022-07-01 16:20:00' and '2022-07-01 23:59:59'
                                                        or  datetime(datetime,'-4 hours') between '2022-07-02 10:00:00' and '2022-07-02 21:00:00'
                                                        or  datetime(datetime,'-4 hours') between '2022-07-03 10:00:00' and '2022-07-03 21:00:00'
                                                        or  datetime(datetime,'-4 hours') between '2022-07-04 10:00:00' and '2022-07-04 21:00:00'
                                                    order by datetime desc""").fetchall()
            data_2022=cursor.execute("""with ranks as
                                        (select upper(Song) as Song
                                        ,upper(Band) as Band
                                        ,datetime
                                        ,421 - ROW_NUMBER() OVER (ORDER BY datetime) as Rank
                                        from july2022
                                        where datetime(datetime,'-4 hours') between '2022-07-01 16:20:00' and '2022-07-01 23:59:59'
                                            or  datetime(datetime,'-4 hours') between '2022-07-02 10:00:00' and '2022-07-02 21:00:00'
                                            or  datetime(datetime,'-4 hours') between '2022-07-03 10:00:00' and '2022-07-03 21:00:00'
                                            or  datetime(datetime,'-4 hours') between '2022-07-04 10:00:00' and '2022-07-04 21:00:00'
                                       order by datetime
                                       limit 420
                                       )
                            select july2022.DateTime
                                            ,time(datetime(july2022.datetime,'-4 hours')) as song_time
                                            ,july2022.Song
                                            ,july2022.Band
                                            ,datetime(july2022.DateTime,'-4 hours') as DateTime_Fixed
                                            ,date(datetime(july2022.DateTime,'-4 hours')) as DatePart
                                            ,july2022.LIKE
                                            ,july2022.trackid
                                            ,july2022.artistid
                                            ,ranks.Rank
                            from july2022
                            inner join ranks
                            on ranks.datetime=july2022.datetime

                                        order by july2022.DateTime desc""").fetchall()

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

@app.route('/song/<trackid>',methods=['GET','POST'])
def song_page(trackid):

    if  request.method=='POST':
        print(request.method)
        print('starting')
        trackid = request.form.get('trackid')
        print("got trackid")
        band = request.form.get('band')
        song = request.form.get('song')
        print("starting")
        conn,engine=create_connection()
        cursor=conn.cursor()
        print("connected")
        comment = request.form.get('comment')
        print("got comment")
        author = request.form.get('author')

        print("Printing the stuff")
        print("{0} {1} {2} {3} {4}".format(comment,author,trackid,song,band))
        conn.execute('INSERT INTO comments (comment,author,DateTime,trackid,comment_type)'
             'VALUES (?, ?, ?, ?, ?)',
                (comment,author,datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),trackid,"song")
                    )
        conn.commit()
        conn.close()
        return redirect(url_for('song_page',trackid=trackid))
    conn,engine=create_connection()
    cursor=conn.cursor()
    song=cursor.execute("select sum(Like) as Like,Song,band,trackid from july2022 where trackid='{0}'".format(trackid)).fetchone()
    comments = cursor.execute("select *,date(datetime) as datetime_fixed from comments where trackid='{}' and comment_type = 'song' order by datetime desc".format(trackid)).fetchall()
    return render_template('song.html',song=song,comments=comments)

@app.route('/artist/<artistid>',methods=['GET','POST'])
def artist_page(artistid):

    if  request.method=='POST':
        print(request.method)
        print('starting')
        artistid = request.form.get('artistid')
        print("got trackid")
        band = request.form.get('band')

        print("starting")
        conn,engine=create_connection()
        cursor=conn.cursor()
        print("connected")
        comment = request.form.get('comment')
        print("got comment")
        author = request.form.get('author')

        print("Printing the stuff")
        print("{0} {1} {2} {3}".format(comment,author,artistid,band))
        conn.execute('INSERT INTO comments (comment,author,DateTime,artistid,comment_type)'
             'VALUES (?, ?, ?, ?, ?)',
                (comment,author,datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),artistid,"artist")
                    )
        conn.commit()
        conn.close()
        return redirect(url_for('artist_page',artistid=artistid))

    conn,engine=create_connection()
    cursor=conn.cursor()
    artist=cursor.execute("select sum(Like) as Like,band,artistid from july2022 where artistid='{0}'".format(artistid)).fetchone()
    comments = cursor.execute("select *,date(datetime) as datetime_fixed from comments where artistid='{}' and comment_type = 'artist' order by datetime desc".format(artistid)).fetchall()
    most_played = cursor.execute("select count(*) as counts,song from july2022 where artistid = '{}' group by song order by count(*) desc limit 3".format(artistid)).fetchall()
    return render_template('artist.html',artist=artist,comments=comments,most_played=most_played)


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
    p = make_agg_plot('today')
    return json.dumps(json_item(p,"myplot3"))

@app.route('/myplot4')
def myplot4():
    p = make_agg_plot('yesterday')
    return json.dumps(json_item(p,"myplot4"))

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
