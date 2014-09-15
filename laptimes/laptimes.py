import MySQLdb
import config
from bottle import route, run, template, debug, view, static_file

@route('/js/<filename>')
def js_static(filename):
    return static_file(filename, root='./static/js')


@route('/img/<filename>')
def img_static(filename):
    return static_file(filename, root='./static/img')


@route('/css/<filename>')
def img_static(filename):
    return static_file(filename, root='./static/css')


@route('/')
@route('/laptimes')
@route('/laptimes/top/<top_num:int>')
def show_laptimes(top_num=25):
    con = MySQLdb.connect(config.opts['mysql']['host'], config.opts['mysql']['username'], config.opts['mysql']['password'], config.opts['mysql']['database']);
    c = con.cursor()
    if top_num > 500:
         top_num = 25
    c.execute('SELECT racers.name, laptimes.laptime, laptimes.datetime \
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


debug(True)
run(reloader=True)
