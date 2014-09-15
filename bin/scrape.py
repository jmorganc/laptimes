import pycurl
import cStringIO
from bs4 import BeautifulSoup
import time
import datetime
import sys
import os
import MySQLdb
import pprint

sys.path.append(os.path.abspath('{0}/../../'.format(os.path.abspath(__file__))))
from laptimes import config


def main():
    soup = scrape()
    rows = parse(soup)
    save(rows)


def scrape():
    response = cStringIO.StringIO()

    c = pycurl.Curl()
    c.setopt(c.URL, 'http://clubspeedtiming.com/dkcdallas/toptime.aspx?&Track=3')
    #c.setopt(c.URL, 'http://localhost/toptime_13.html')
    c.setopt(c.USERAGENT, 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36')
    c.setopt(c.VERBOSE, False)
    c.setopt(c.WRITEFUNCTION, response.write)
    c.perform()
    c.close()

    html = response.getvalue()

    return BeautifulSoup(html)


def parse(soup):
    rows = []
    rowtypes = ['TableSelectedItemStyle', 'TableItemStyle', 'AlternateItemStyle']
    for rowtype in rowtypes:
        for row in soup.find_all('tr', class_=rowtype):
            soup_row = BeautifulSoup(str(row))
            tr = soup_row.find('tr').contents
            row_name = tr[2].contents[1].contents[0]
            row_laptime = tr[3].contents[1].contents[0]
            row_laptime_split = row_laptime.split(':')
            row_datetime = str(tr[4].contents[0]).replace('\n', '').replace('\t', '').replace('\r', '')
            rows.append({
                'name': row_name,
                'laptime': int(row_laptime_split[0]) * 60 + int(row_laptime_split[1]) + int(row_laptime_split[2]) / 1000.0,
                #'date_time': time.strptime("9/14/2014 5:18 PM", '%m/%d/%Y %I:%M %p')
                'date_time': time.strptime(row_datetime, '%m/%d/%Y %I:%M %p')
            })

    return rows


def save(rows):
    """
    If the user does not exist, create them
        Then record their time
    If the user does exist and they do not have a time for this date_time, save that time
    """
    connection = MySQLdb.connect(config.opts['mysql']['host'], config.opts['mysql']['username'], config.opts['mysql']['password'], config.opts['mysql']['database'])
    cursor = connection.cursor()

    for row in rows:
        racer_id = create_user(row['name'], cursor)
        save_laptime(racer_id, row['laptime'], row['date_time'], cursor)

    connection.commit()
    cursor.close()
    connection.close()


def create_user(name, cursor):
    cursor.execute('SELECT id FROM racers WHERE name = %s', (name,))
    racer_id = cursor.fetchone()

    if not racer_id:
        cursor.execute('INSERT INTO racers(name) VALUES(%s)', (name,))
        racer_id = cursor.lastrowid
        print 'Racer \'{0}\' ({1}) created.'.format(name, racer_id)
    else:
        racer_id = int(racer_id[0])

    return racer_id


def save_laptime(racer_id, laptime, date_time, cursor):
    date_time = datetime.datetime(date_time.tm_year, date_time.tm_mon, date_time.tm_mday, date_time.tm_hour, date_time.tm_min)
    date_time_str = date_time.strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('SELECT racer_id, laptime, datetime \
                    FROM laptimes \
                    WHERE racer_id = %s \
                    AND laptime = %s \
                    AND datetime = %s', (racer_id, laptime, date_time_str))
    row = cursor.fetchone()

    if not row:
        '''User, laptime and datetime not found, so this is a unique lap.'''
        cursor.execute('INSERT INTO laptimes(racer_id, laptime, datetime) \
                        VALUES(%s, %s, %s)', (racer_id, laptime, date_time))
        print 'Laptime created: ({0}, {1}, {2})'.format(racer_id, laptime, date_time)


if __name__ == '__main__':
    sys.exit(main())
