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
def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect("/home/terrysey/july420/DB/july420.db"
        ,detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory=sqlite3.Row
        return conn

    except Error as e:
        #print(e)
        try:
            conn = sqlite3.connect("DB/july420.db"
            ,detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory=sqlite3.Row
            return conn
        except Error as e:
            #print(e)
colormap = {'setosa': 'red', 'versicolor': 'green', 'virginica': 'blue'}
colors = [colormap[x] for x in flowers['species']]

def make_plot(x, y):
    p = figure(title = "Iris Morphology", sizing_mode="fixed", width=400, height=400)
    p.xaxis.axis_label = x
    p.yaxis.axis_label = y
    p.circle(flowers[x], flowers[y], color=colors, fill_alpha=0.2, size=10)
    return p
# def make_plot(df):
#     p = figure(x_range=df['Band'].head(10), height=500, title="July 420 Top 10 Bands 2020",toolbar_location=None, tools="")
#     p.vbar(x=df['Band'].head(10), top=df['volume'].head(10), width=0.9)
#     p.xaxis.major_label_orientation = math.pi/6
#     return p
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


@app.route('/plot')
def plot():
    return render_template('plot.html',resources=CDN.render())

@app.route('/myplot')
def myplot():
    # conn = create_connection()
    # agg_sql = """select count(*) as volume
    #             ,band
    #             ,year
    #     from july420
    #     where year ='2020'
    #     group by band, year
    #     order by count(*) desc"""
    # df = pd.read_sql(agg_sql,conn)
    p = make_plot('petal_width', 'petal_length')
    #return p
    return json.dumps(json_item(p))




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
