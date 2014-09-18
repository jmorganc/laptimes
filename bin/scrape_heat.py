import pycurl
import cStringIO
from bs4 import BeautifulSoup
import time
import datetime
import sys
import os
import MySQLdb
import re
import pprint

sys.path.append(os.path.abspath('{0}/../../'.format(os.path.abspath(__file__))))
from laptimes import config


def main():
    heat_id = 27040
    soup = scrape(heat_id)
    racer_ids = get_ids(soup)
    #pprint.pprint(racer_ids)
    heat_info, heat_laptimes = parse(soup, racer_ids, heat_id)
    #pprint.pprint(heat_info)
    pprint.pprint(heat_laptimes)
    sys.exit()
    save(heat_info, heat_laptimes)


def scrape(id, page='HeatDetails.aspx?HeatNo='):
    response = cStringIO.StringIO()

    c = pycurl.Curl()
    c.setopt(c.URL, 'http://clubspeedtiming.com/dkcdallas/{0}{1}'.format(page, id))
    c.setopt(c.USERAGENT, 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36')
    c.setopt(c.VERBOSE, False)
    c.setopt(c.WRITEFUNCTION, response.write)
    c.perform()
    c.close()

    html = response.getvalue()

    return BeautifulSoup(html)


def get_ids(soup):
    racer_ids = {}
    racer_links = soup.find_all('a', {'href': re.compile(r'RacerHistory\.aspx\?CustID=[0-9]*')})
    for racer in racer_links:
        racer = str(racer).strip('<a href="RacerHistory.aspx?CustID=').strip('</a>')
        racer_split = racer.split('">')
        racer_id = racer_split[0]
        racer_name = racer_split[1]
        kart_ids = []

        soup = scrape(racer_id, 'RacerHistory.aspx?CustID=')
        racer_full_name = soup.find('span', {'id': 'lblRacerName'}).contents[0]
        heat_rows = soup.find_all('tr', class_='Normal')
        for row in heat_rows:
            kart_id = row.td.a.contents[0]
            kart_id = kart_id.split(' - Kart ')[1]
            datetime = row.td.next_sibling.contents[0].strip('\r').strip('\n').strip('\t').strip('\r\n')
            kart_ids.append({datetime: kart_id})

        racer_ids[racer_name] = {'id': racer_id, 'full_name': racer_full_name, 'kart_ids': kart_ids}

    return racer_ids


def parse(soup, racer_ids, heat_id):
    heat_type = soup.find('span', {'id': 'lblRaceType'}).contents[0]
    heat_win_by = soup.find('span', {'id': 'lblWinnerBy'}).contents[0]
    heat_date = soup.find('span', {'id': 'lblDate'}).contents[0]
    heat_winner = soup.find('span', {'id': 'lblWinner'}).contents[0]
    heat_info = {
            'id': heat_id,
            'type': heat_type,
            'win_by': heat_win_by,
            'date': heat_date,
            'winner': racer_ids[heat_winner]['id']
        }

    heat_laptimes = {}
    soup_tables = soup.find_all('table', class_='LapTimes')
    for table in soup_tables:
        soup_table = BeautifulSoup(str(table))

        racer_name = soup_table.thead.tr.th.contents[0]

        kart_id = -1
        for date_kart in racer_ids[racer_name]['kart_ids']:
            if heat_date in date_kart:
                kart_id = date_kart[heat_date]
                break

        soup_rows = soup_table.tbody.find_all('tr')
        for lap in soup_rows:
            second_td = lap.td.next_sibling
            try:
                int(second_td.contents[0][0])
                time_position = second_td.contents[0].split(' ')
                lap_num = lap.td.contents[0]
                laptime = time_position[0]
                position = time_position[1].strip('[').strip(']')

                info = {
                    'heat_id': heat_id,
                    'kart_id': kart_id,
                    'lap_number': lap_num,
                    'laptime': laptime,
                    'position': position
                }
                if racer_ids[racer_name]['id'] not in heat_laptimes:
                    heat_laptimes[racer_ids[racer_name]['id']] = [info]
                else:
                    heat_laptimes[racer_ids[racer_name]['id']].append(info)
            except ValueError:
                continue

    return heat_info, heat_laptimes


def save(heat_info, heat_laptimes):
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
