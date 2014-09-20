#!/usr/bin/python

import urllib2
from bs4 import BeautifulSoup
import time
import datetime
import MySQLdb
import sys, os

sys.path.append(os.path.abspath('{0}/../../'.format(os.path.abspath(__file__))))
from laptimes import config


def main():
	while True:
		racer_id = thread_control()
		if racer_id:
			print 'processing racer {0}'.format(str(racer_id))
			races = get_races(str(racer_id))

			for race in races:
				laptimes = get_laptimes(race['racer_id'], race['race_id'])
				race['laptimes'] = laptimes[0]
				race_datetime = time.strptime(laptimes[1], '%m/%d/%Y %I:%M %p')
				race['race_date'] = race_datetime
				mysql_save(race)

		else:
			print 'no racers to process'
			time.sleep(60)


def get_races(racer_id):
	url = "http://clubspeedtiming.com/dkcdallas/RacerHistory.aspx?CustID="+racer_id

	page = urllib2.urlopen(url).read()
	soup = BeautifulSoup(page)

	links = soup.find_all('a')
	races = []

	for link in links:
		race = {}
		racer_name = soup.find('span', attrs={'id':'lblRacerName'})
		heat_type_string = link.get_text()[:23]
		kart_id = link.get_text()[31:]
		race_id = str(link.get('href'))[24:]
		race['race_id'] = race_id
		race['kart_id'] = kart_id
		racer_name_str = unicode(racer_name.get_text().strip().replace('\n', '').replace('\t', '').replace('\r', ''))
		race['racer_name'] = racer_name_str.encode('utf-8')
		race['racer_id'] = racer_id

		if heat_type_string == '10 min Adult Super Heat':
			races.append(race)

	return races


def get_laptimes(racer_id, race_id):
	url = "http://clubspeedtiming.com/dkcdallas/HeatDetails.aspx?HeatNo="+race_id

	page = urllib2.urlopen(url).read()
	soup = BeautifulSoup(page)

	racers = []
	laptimes = []
	race_date_span = soup.find('span', attrs={'id':'lblDate'})
	race_date = race_date_span.get_text()

	links = soup.find_all('a')
	for link in links:
		racers.append(int((link.get('href')[25:])))

	racer_index = (sorted(racers).index(int(racer_id))+3)

	tables = soup.find_all('table')

	racer_table = tables[(racer_index)]

	tds = racer_table.find_all('td')[1::2]
	for td in tds:
		laptime = td.get_text().split()
		if laptime:
			laptimes.append(laptime[0])

	return laptimes, race_date


def mysql_save(race):
	connection = mysql_connect()
	cursor = connection.cursor()

	date_time = race['race_date']
	date_time = datetime.datetime(date_time.tm_year, date_time.tm_mon, date_time.tm_mday, date_time.tm_hour, date_time.tm_min)

	create_racer(race['racer_id'], race['racer_name'], cursor)
	create_kart(race['kart_id'], cursor)
	create_race(race['race_id'], race['race_date'], cursor)

	for laptime in race['laptimes']:
		laptime_index = race['laptimes'].index(laptime)
		time_shift = 0
		i = 0

		if laptime_index == 0:
			time_shift = round(float(laptime))
		else:
			while (i < laptime_index):
				time_shift += round(float(race['laptimes'][i]))
				i += 1
		date_time = date_time + datetime.timedelta(seconds=time_shift)

		create_laptime(race['racer_id'], race['kart_id'], race['race_id'], (laptime_index+1), laptime, date_time, cursor)

	update_queue(race['racer_id'], cursor)
	connection.commit()
	cursor.close()
	connection.close()


def create_racer(racer_id, racer_name, cursor):
	cursor.execute('LOCK TABLE racers write')
	cursor.execute('SELECT id FROM racers WHERE id = %s', (racer_id,))

	result = cursor.fetchone()

	if not result:
		cursor.execute('INSERT INTO racers(id, racer_name) VALUES(%s, %s)', (racer_id, racer_name,))
		print 'Racer {0} created.'.format(racer_name)
	cursor.execute('UNLOCK TABLES')


def create_kart(kart_id, cursor):
	cursor.execute('LOCK TABLE karts write')
	cursor.execute('SELECT id FROM karts WHERE id = %s', (kart_id,))

	result = cursor.fetchone()

	if not result:
		cursor.execute('INSERT INTO karts(id) VALUES(%s)', (kart_id,))
		print 'Kart {0} created.'.format(kart_id,)
	cursor.execute('UNLOCK TABLES')


def create_race(race_id, date_time, cursor):
	cursor.execute('LOCK TABLE races write')
	cursor.execute('SELECT id FROM races WHERE id = %s', (race_id,))

	result = cursor.fetchone()
	date_time = datetime.datetime(date_time.tm_year, date_time.tm_mon, date_time.tm_mday, date_time.tm_hour, date_time.tm_min)

	if not result:
		cursor.execute('INSERT INTO races(id, datetime) VALUES(%s, %s)', (race_id, date_time,))
		print 'Race {0} created.'.format(race_id,)
	cursor.execute('UNLOCK TABLES')


def create_laptime(racer_id, kart_id, race_id, lap_number, laptime, date_time, cursor):
	date_time_str = date_time.strftime('%Y-%m-%d %H:%M:%S')

	cursor.execute('LOCK TABLE laptimes write')
	cursor.execute('SELECT racer_id, kart_id, race_id, lap_number, laptime \
					FROM laptimes \
					WHERE racer_id = %s \
					AND kart_id = %s \
					AND race_id = %s \
					AND lap_number = %s', (racer_id, kart_id, race_id, lap_number,))

	result = cursor.fetchone()

	if not result:
		cursor.execute('INSERT INTO laptimes(racer_id, kart_id, race_id, lap_number, laptime, datetime) \
						VALUES(%s, %s, %s, %s, %s, %s)', (racer_id, kart_id, race_id, lap_number, laptime, date_time,))
		print 'Laptime created: ({0}, {1}, {2})'.format(racer_id, laptime, date_time)
	cursor.execute('UNLOCK TABLES')


def update_queue(racer_id, cursor):
	cursor.execute('LOCK TABLE threading WRITE')
	cursor.execute('UPDATE threading \
					SET processing = -1, processing_finished = NOW() \
					WHERE id = %s', (racer_id),)
	cursor.execute('UNLOCK TABLES')



def thread_control():
	connection = mysql_connect()
	cursor = connection.cursor()

	cursor.execute('LOCK TABLE threading WRITE')
	cursor.execute('SELECT id FROM threading \
					WHERE processing = 0 \
					LIMIT 1')

	result = cursor.fetchone()

	if result:
		racer_id = result[0]

		cursor.execute('UPDATE threading \
						SET processing = 1, processing_started = NOW() \
						WHERE id = %s', (racer_id),)
		connection.commit()
		cursor.execute('UNLOCK TABLES')
		cursor.close()
		connection.close()

		return racer_id
	else:
		cursor.execute('UNLOCK TABLES')
		cursor.close()
		connection.close()


def mysql_connect():
	return MySQLdb.connect(config.opts['mysql']['host'], config.opts['mysql']['username'], config.opts['mysql']['password'], config.opts['mysql']['database'])


main()
