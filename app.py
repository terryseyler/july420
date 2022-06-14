from flask import Flask
import sqlite3
from sqlite3 import Error
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
app.config['SECRET_KEY']='bb2f7df67e28dcfbeb850ae976fdaea6'
def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect("/home/terrysey/july420/DB/july420.db"
        ,detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory=sqlite3.Row
        return conn

    except Error as e:
        print(e)
        try:
            conn = sqlite3.connect("DB/july420.db"
            ,detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory=sqlite3.Row
            return conn
        except Error as e:
            print(e)
colormap = {'setosa': 'red', 'versicolor': 'green', 'virginica': 'blue'}
colors = [colormap[x] for x in flowers['species']]

def make_agg_plot(year):
    conn = create_connection()
    agg_sql = """select count(*) as volume
                ,band
                ,year
        from july420
        where year ='{}'
        group by band, year
        order by count(*) desc""".format(year)
    df = pd.read_sql(agg_sql,conn)
    p = figure(x_range=df['Band'].head(10), height=500, title="July 420 Top 10 Bands {}".format(year),toolbar_location=None, tools="")
    p.vbar(x=df['Band'].head(10), top=df['volume'].head(10), width=0.9)
    p.xaxis.major_label_orientation = math.pi/6
    return p
@app.route('/')
def index():
    conn = create_connection()
    cursor=conn.cursor()

    data_2020 = cursor.execute("""select * from july420 where year = '2020'""").fetchall()

    data_2021 = cursor.execute("""select * from july420 where year = '2021'""").fetchall()

    return render_template('index.html',data_2020=data_2020,data_2021=data_2021)

@app.route("/",methods=['POST'])
def song_search():
    if request.method=='POST':
        if request.form['submit_button'] == 'Search Song':
            song=request.form['song']
            conn=create_connection()
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
            conn=create_connection()
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
            conn = create_connection()
            cursor=conn.cursor()
            data_2020 = cursor.execute("""select * from july420 where year = '2020'""").fetchall()
            data_2021 = cursor.execute("""select * from july420 where year = '2021'""").fetchall()

            return render_template('index.html',data_2020=data_2020,data_2021=data_2021)

@app.route('/2022')
def twentytwentytwo():
    conn=create_connection()
    cursor=conn.cursor()
    data_2022=cursor.execute("""select * from july420 where year='2022'""").fetchall()
    return render_template('2022.html',data_2022=data_2022)

@app.route('/2022',methods=['POST','GET'])
def add_song():
    conn=create_connection()
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

    return redirect(url_for('twentytwentytwo'))

@app.route('/delete/<int:Rank>')
def delete(Rank):
    conn=create_connection()
    cursor=conn.cursor()
    cursor.execute("DELETE from july420 where rank= '{}' and year ='2022'".format(Rank))
    conn.commit()
    return redirect(url_for('twentytwentytwo'))



@app.route('/plot')
def plot():
    return render_template('plot.html',resources=CDN.render())

@app.route('/myplot')
def myplot():

    p = make_agg_plot('2020')
    #return p
    return json.dumps(json_item(p,"myplot"))

@app.route('/myplot2')
def myplot2():

    p = make_agg_plot('2021')
    #return p
    return json.dumps(json_item(p,"myplot2"))




#might need this query later?
    # data_agg = cursor.execute("""select data_2020.Rank as Rank
    #                             ,data_2020.Song as song_2020
    #                             ,data_2020.Band as band_2020
    #                             ,data_2021.Song as song_2021
    #                             ,data_2021.Band as band_2021
    #                             from
    #                                 (select * from july420 where year='2020') as data_2020
    #                             inner JOIN
    #                                 (select * from july420 where year='2021') as data_2021
    #                             on data_2020.Rank = data_2021.Rank
    #                             """).fetchall()
