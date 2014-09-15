import MySQLdb
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

@route('/laptimes')
def show_laptimes():
  con = MySQLdb.connect('');
  c = con.cursor()
  c.execute("select racers.name, laptimes.laptime from laptimes inner join racers on laptimes.racer_id=racers.id order by laptime limit 25")
  data = c.fetchall()
  c.close()
  output = template('templates/laptimes', rows=data)
  return output

debug(True)
run(reloader=True)