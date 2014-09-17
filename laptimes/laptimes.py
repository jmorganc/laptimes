import MySQLdb, MySQLdb.cursors
import config
from bottle import route, run, template, debug, view, static_file, request


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
def racer_profile(id):
    con = mysql_connect()
    c = con.cursor()

    c.execute('SELECT * \
                FROM racers \
                WHERE id = %s', (id,))
    racer = c.fetchone()

    c.execute('SELECT id, laptime, datetime, created \
                FROM laptimes \
                WHERE racer_id = %s \
                ORDER BY datetime ASC', (id,))
    laps = c.fetchall()

    c.close()
    con.close()
    return template('templates/racer_profile', racer=racer, laps=laps)


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
        		WHERE name LIKE %s', ('%' + racer_name + '%',))
    racers = c.fetchall()
    c.close()
    con.close()
    return template('templates/search', racers=racers)


@route('/')
@route('/laptimes')
@route('/laptimes/top/<top_num:int>')
@route('/laptimes/date/<year:int>')
@route('/laptimes/date/<year:int>/<month:int>')
@route('/laptimes/date/<year:int>/<month:int>/<day:int>')
def show_laptimes(top_num=10, year=0, month=0, day=0):
    con = mysql_connect()
    c = con.cursor()

    sql_params = (top_num,)

    date_sql = ''
    if year > 0:
        date_sql = 'AND laptimes.datetime >= "%s-01-01 00:00:00" \
                    AND laptimes.datetime < "%s-01-01 00:00:00"'
        sql_params = (year, year + 1, top_num)
        if month > 0:
            date_sql = 'AND laptimes.datetime >= "%s-%s-01 00:00:00" \
                    AND laptimes.datetime < "%s-%s-01 00:00:00"'
            sql_params = (year, month, year, month + 1, top_num)
            if day > 0:
                date_sql = 'AND laptimes.datetime >= "%s-%s-%s 00:00:00" \
                    AND laptimes.datetime < "%s-%s-%s 00:00:00"'
                sql_params = (year, month, day, year, month, day + 1, top_num)

    query = 'SELECT racers.id, racers.name, laptimes.laptime, laptimes.datetime \
                FROM laptimes \
                INNER JOIN racers ON laptimes.racer_id = racers.id \
                WHERE 1=1 \
                {0}\
                ORDER BY laptime ASC \
                LIMIT %s'.format(date_sql)
    print query
    print sql_params
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
    average = round((average / top_num), 3)

    return template('templates/laptimes', rows=data, top_num=top_num, average=average, weather_summary=weather_data)


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
    c.execute('SELECT weather \
        		FROM weather \
        		WHERE observation_time < %s \
                ORDER BY observation_time DESC \
                LIMIT 1', (datetime,))
    weather = c.fetchone()
    c.close()
    con.close()

    if weather:
        return weather
    return {'weather': 'No data recorded'}


# Set up the MySQL connection: host, user, pass, db, parameter to allow for a dictionary to be returned rather than a tuple
def mysql_connect(host=config.opts['mysql']['host'], username=config.opts['mysql']['username'], password=config.opts['mysql']['password'], database=config.opts['mysql']['database']):
    return MySQLdb.connect(host, username, password, database, cursorclass=MySQLdb.cursors.DictCursor)

debug(True)
run(reloader=True)
