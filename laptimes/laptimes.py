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
                WHERE racer_id = %s', (id,))
    laps = c.fetchall()

    c.close()
    con.close()
    return template('templates/racer_profile', racer=racer, laps=laps)


@route('/search_racers')
def search():
	return template('templates/search')


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
	return template('templates/search_results', racers=racers)


@route('/')
@route('/laptimes')
@route('/laptimes/top/<top_num:int>')
def show_laptimes(top_num=25):
    con = mysql_connect()
    c = con.cursor()
    if top_num > 500:
         top_num = 25
    c.execute('SELECT racers.id, racers.name, laptimes.laptime, laptimes.datetime \
                FROM laptimes \
                INNER JOIN racers ON laptimes.racer_id = racers.id \
                ORDER BY laptime ASC \
                LIMIT %s', (top_num,))
    data = c.fetchall()
    c.close()
    con.close()

    return template('templates/laptimes', rows=data, top_num=top_num)


@route('/about')
def about():
    return template('templates/about')


@route('/contact')
def contact():
    return template('templates/contact')


# Set up the MySQL connection: host, user, pass, db, parameter to allow for a dictionary to be returned rather than a tuple
def mysql_connect(host=config.opts['mysql']['host'], username=config.opts['mysql']['username'], password=config.opts['mysql']['password'], database=config.opts['mysql']['database']):
    return MySQLdb.connect(host, username, password, database, cursorclass=MySQLdb.cursors.DictCursor)


debug(True)
run(reloader=True)
