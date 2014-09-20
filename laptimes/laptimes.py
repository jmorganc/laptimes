import MySQLdb, MySQLdb.cursors
import config
from bottle import route, run, template, debug, view, static_file, request
import time
import re


@route('/js/<filename>')
def js_static(filename):
    return static_file(filename, root='./static/js')


@route('/img/<filename>')
def img_static(filename):
    return static_file(filename, root='./static/img')


@route('/css/<filename>')
def img_static(filename):
    return static_file(filename, root='./static/css')


@route('/fonts/<filename>')
def font_static(filename):
    return static_file(filename, root='./static/fonts')


@route('/racer/<id:int>')
@route('/racer/<id:int>/kart/<kart_id:int>')
@route('/racer/<id:int>/heat/<heat_id:int>')
def racer_profile(id, kart_id=-1, heat_id=-1):
    con = mysql_connect()
    c = con.cursor()

    c.execute('SELECT * \
                FROM racers \
                WHERE id = %s', (id,))
    racer = c.fetchone()
    if not racer:
        return template('templates/404')

    #racer['racer_name'] = re.sub('[(){}<>:.]', '', racer['racer_name'])
    #racer['racer_name'] = racer['racer_name'].strip(u'\xa0')

    c.execute('SELECT DISTINCT(kart_id)\
                FROM laptimes\
                WHERE racer_id = %s\
                ORDER BY kart_id ASC', (id,))
    karts = c.fetchall()

    c.execute('SELECT DISTINCT(l.race_id), r.datetime\
                FROM laptimes l\
                LEFT JOIN races r ON r.id = l.race_id\
                WHERE l.racer_id = %s\
                ORDER BY race_id ASC', (id,))
    heats = c.fetchall()

    param_sql = ''
    sql_params = (id,)
    if kart_id > -1:
        param_sql = 'AND kart_id = %s'
        sql_params = (id, kart_id)

    if heat_id > -1:
        param_sql = 'AND race_id = %s'
        sql_params = (id, heat_id)

    c.execute('SELECT id, kart_id, race_id, lap_number, laptime, datetime, created \
                FROM laptimes \
                WHERE racer_id = %s \
                {0} \
                ORDER BY datetime ASC'.format(param_sql), sql_params)
    laps = c.fetchall()

    weather_data = {}
    for row in laps:
        weather_data[row['id']] = get_weather(row['datetime'])
    print(weather_data)

    c.close()
    con.close()
    return template('templates/racer_profile', racer=racer, laps=laps, karts=karts, kart_id=kart_id, heats=heats, heat_id=heat_id, weather_data=weather_data)


@route('/search_racers')
def search():
    return template('templates/search', racers=None)


@route('/search_racers', method='POST')
def search_racers():
    racer_name = request.forms.get('racer_name')
    con = mysql_connect()
    c = con.cursor()
    c.execute('SELECT * \
        		FROM racers \
        		WHERE racer_name LIKE %s', ('%' + racer_name + '%',))
    racers = c.fetchall()
    c.close()
    con.close()
    return template('templates/search', racers=racers)


@route('/')
@route('/laptimes')
@route('/laptimes/top/<top_num:int>')
@route('/laptimes/date/<year:int>')
@route('/laptimes/date/<year:int>/top/<top_num:int>')
@route('/laptimes/date/<year:int>/<month:int>')
@route('/laptimes/date/<year:int>/<month:int>/top/<top_num:int>')
@route('/laptimes/date/<year:int>/<month:int>/<day:int>')
@route('/laptimes/date/<year:int>/<month:int>/<day:int>/top/<top_num:int>')
def show_laptimes(top_num=10, year=0, month=0, day=0):
    con = mysql_connect()
    c = con.cursor()

    date = (year, month, day)
    sql_params = (top_num,)

    date_sql = ''
    if year > 0:
        date_sql = 'AND l.datetime >= "%s-01-01 00:00:00" \
                    AND l.datetime < "%s-01-01 00:00:00"'
        sql_params = (year, year + 1, top_num)
        if month > 0:
            date_sql = 'AND l.datetime >= "%s-%s-01 00:00:00" \
                    AND l.datetime < "%s-%s-01 00:00:00"'
            sql_params = (year, month, year, month + 1, top_num)
            if day > 0:
                date_sql = 'AND l.datetime >= "%s-%s-%s 00:00:00" \
                    AND l.datetime < "%s-%s-%s 00:00:00"'
                sql_params = (year, month, day, year, month, day + 1, top_num)

    query = 'SELECT l.id, l.racer_id, r.racer_name, l.kart_id, l.race_id, l.lap_number, l.laptime, l.datetime \
                FROM laptimes l \
                LEFT JOIN racers r ON r.id = l.racer_id \
                WHERE l.laptime > 0.000 \
                {0} \
                ORDER BY laptime ASC \
                LIMIT %s'.format(date_sql)
    # query = 'SELECT racers.id, racers.name, laptimes.laptime, laptimes.datetime \
    #             FROM laptimes \
    #             INNER JOIN racers ON laptimes.racer_id = racers.id \
    #             WHERE 1=1 \
    #             {0}\
    #             ORDER BY laptime ASC \
    #             LIMIT %s'.format(date_sql)
    c.execute(query, sql_params)
    data = c.fetchall()
    c.close()
    con.close()

    top_num = len(data)
    average = 0.0
    weather_data = {}
    for row in data:
        average += row['laptime']
        weather = get_weather(row['datetime'])
        weather_data[row['id']] = weather

    if top_num > 0:
        average = round((average / top_num), 3)

    current_date = time.strftime('%Y-%m-%d')

    return template('templates/laptimes', rows=data, top_num=top_num, average=average, weather_data=weather_data, date=date, current_date=current_date)


@route('/about')
def about():
    return template('templates/about')


@route('/contact')
def contact():
    return template('templates/contact')


# Get nearest observed weather based on a provided datetime
def get_weather(datetime):
    con = mysql_connect()
    c = con.cursor()
    c.execute('SELECT weather AS Weather, temp_f AS Temperature, relative_humidity AS Humidity, wind_dir, wind_mph \
                FROM weather \
                WHERE observation_time <= %s \
                ORDER BY observation_time DESC \
                LIMIT 1', (datetime,))
    weather = c.fetchone()
    c.close()
    con.close()

    if weather:
        return weather
    return {}


# Set up the MySQL connection: host, user, pass, db, parameter to allow for a dictionary to be returned rather than a tuple
def mysql_connect(host=config.opts['mysql']['host'], username=config.opts['mysql']['username'], password=config.opts['mysql']['password'], database=config.opts['mysql']['database']):
    return MySQLdb.connect(host, username, password, database, cursorclass=MySQLdb.cursors.DictCursor)

debug(True)
run(reloader=True)
