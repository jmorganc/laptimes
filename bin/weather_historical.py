"""
Scrape weather from Weather Underground
"""

import sys
import os
import requests
import datetime
import time
import MySQLdb
import pprint

sys.path.append(os.path.abspath('{0}/../../'.format(os.path.abspath(__file__))))
from laptimes import config


def main():
    date_start = datetime.date(2013, 9, 30)
    date_end = datetime.date(2013, 12, 31)
    #date_end = datetime.date(2014, 9, 15)

    while date_start != date_end:
        print 'Processing:', date_start
        sys.stdout.flush()
        year = date_start.year
        month = date_start.month
        day = date_start.day

        if month < 10:
            month = '0{0}'.format(month)
        if day < 10:
            day = '0{0}'.format(day)

        weather_date = (year, month, day)
        weather_json = get_weather('Caddo Mills, TX', weather_date)
        weather_dict = parse_weather(weather_json)
        save_weather(weather_dict)

        date_start += datetime.timedelta(days=1)
        print 'Sleeping for a minute.\n'
        sys.stdout.flush()        
        time.sleep(70)


def get_weather(citystate, weather_date):
    city, state = parse_citystate(citystate)
    url = 'http://api.wunderground.com/api/{0}/history_{1}{2}{3}/q/{4}/{5}.json'.format(
            config.opts['wunderground']['apikey'],
            weather_date[0],
            weather_date[1],
            weather_date[2],
            state,
            city
    )

    r = requests.get(url)
    if r.status_code != 200:
        r.raise_for_status()

    return r.json()


def parse_citystate(citystate):
    citystate_split = citystate.split(',')
    city = citystate_split[0].replace(' ', '_')
    state = citystate_split[1].strip()

    return (city, state)


def parse_weather(weather_json):
    wdict = weather_json['history']['observations']

    weather_data = []
    dont_want = ['fog', 'hail', 'icon', 'metar', 'thunder', 'tornado', 'utcdate']
    for weather in wdict:
        wants_formatted = {}
        for key, value in weather.iteritems():
            if key in dont_want:
                continue
            if value in ['-9999.00', '-9999.0', '-9999', '-999']: value = None
            if key == 'date':
                value = '{0}-{1}-{2} {3}:{4}:00'.format(
                    value['year'],
                    value['mon'],
                    value['mday'],
                    value['hour'],
                    value['min']
                )
            wants_formatted[str(key)] = value
        weather_data.append(wants_formatted)

    return weather_data


def save_weather(weather_data):
    connection = MySQLdb.connect(config.opts['mysql']['host'], config.opts['mysql']['username'], config.opts['mysql']['password'], config.opts['mysql']['database'])
    cursor = connection.cursor()

    query = 'INSERT INTO weather(\
                dewpoint_c, dewpoint_f, heat_index_c, heat_index_f, observation_time,\
                precip_1hr_in, precip_1hr_metric, precip_today_in, pressure_in, pressure_mb,\
                relative_humidity, temp_c, temp_f, visibility_km, visibility_mi,\
                weather, wind_degrees, wind_dir, wind_kph, wind_mph,\
                windchill_c, windchill_f, wind_gust_kph, wind_gust_mph\
            )\
            VALUES(\
                %s, %s, %s, %s, %s,\
                %s, %s, %s, %s, %s,\
                %s, %s, %s, %s, %s,\
                %s, %s, %s, %s, %s,\
                %s, %s, %s, %s\
            )'

    for weather in weather_data:
        exists = cursor.execute('SELECT id FROM weather WHERE observation_time = %s', (weather['date'],))
        if exists:
            print 'Weather already recorded for this date and time:', weather['date']
            continue
        cursor.execute(query, (
            weather['dewptm'], weather['dewpti'], weather['heatindexm'], weather['heatindexi'], weather['date'],
            weather['precipi'], weather['precipm'], weather['rain'], weather['pressurei'], weather['pressurem'],
            weather['hum'], weather['tempm'], weather['tempi'], weather['vism'], weather['visi'],
            weather['conds'], weather['wdird'], weather['wdire'], weather['wspdm'], weather['wspdi'],
            weather['windchillm'], weather['windchilli'], weather['wgustm'], weather['wgusti']
        ))

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    sys.exit(main())
