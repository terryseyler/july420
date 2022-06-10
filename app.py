from flask import Flask
import sqlite3
from sqlite3 import Error
app= Flask(__name__)
from flask import current_app, g
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect("DB/july420.db"
        ,detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory=sqlite3.Row
    except Error as e:
        print(e)
    return conn

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
