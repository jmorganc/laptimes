"""
Scrape weather from Weather Underground
"""

import sys
import requests
import datetime
import MySQLdb
import rfc822
import config
import pprint


def main():
    weather_json = get_weather('Caddo Mills, TX')
    weather_dict = parse_weather(weather_json)
    pprint.pprint(weather_dict)
    save_weather(weather_dict)


def get_weather(citystate):
    city, state = parse_citystate(citystate)
    url = 'http://api.wunderground.com/api/{0}/conditions/q/{1}/{2}.json'.format(config.opts['wunderground']['apikey'], state, city)
    r = requests.get(url)
    if r.status_code != 200:
        r.raise_for_status()

    # return {u'current_observation': {u'heat_index_c': u'NA', u'local_tz_long': u'America/Chicago', u'observation_location': {u'city': u'Rockwall / Hunt Counties, From The Caddo Mills Area', u'full': u'Rockwall / Hunt Counties, From The Caddo Mills Area, Texas', u'elevation': u'474 ft', u'country': u'US', u'longitude': u'-96.196167', u'state': u'Texas', u'country_iso3166': u'US', u'latitude': u'33.024666'}, u'weather': u'Partly Cloudy', u'local_time_rfc822': u'Mon, 15 Sep 2014 10:23:51 -0500', u'forecast_url': u'http://www.wunderground.com/US/TX/Caddo_Mills.html', u'windchill_c': u'NA', u'estimated': {}, u'windchill_f': u'NA', u'pressure_in': u'30.16', u'dewpoint_string': u'76 F (25 C)', u'solarradiation': u'--', u'ob_url': u'http://www.wunderground.com/cgi-bin/findweather/getForecast?query=33.024666,-96.196167', u'local_epoch': u'1410794631', u'icon_url': u'http://icons.wxug.com/i/c/k/partlycloudy.gif', u'display_location': {u'city': u'Caddo Mills', u'full': u'Caddo Mills, TX', u'magic': u'1', u'state_name': u'Texas', u'zip': u'75135', u'country': u'US', u'longitude': u'-96.23010254', u'state': u'TX', u'wmo': u'99999', u'country_iso3166': u'US', u'latitude': u'33.07109833', u'elevation': u'158.00000000'}, u'precip_today_string': u'0.00 in (0 mm)', u'dewpoint_f': 76, u'dewpoint_c': 25, u'precip_today_metric': u'0', u'feelslike_c': u'24.6', u'image': {u'url': u'http://icons.wxug.com/graphics/wu2/logo_130x80.png', u'link': u'http://www.wunderground.com', u'title': u'Weather Underground'}, u'wind_mph': 1.0, u'wind_gust_kph': u'6.4', u'feelslike_f': u'76.3', u'local_tz_short': u'CDT', u'precip_today_in': u'0.00', u'heat_index_f': u'NA', u'nowcast': u' A line of rain showers extending from Paris to Fort Worth to\nComanche continues to push eastward around 25 mph. Other\nareas across central Texas may see scattered showers and drizzle\nthrough the morning hours. Elsewhere...skies will remain mostly\ncloudy through the morning with temperatures in the upper 60s\nand lower 70s. Winds will be light out of the south.', u'temp_f': 76.3, u'station_id': u'KTXROCKW1', u'windchill_string': u'NA', u'temp_c': 24.6, u'visibility_km': u'16.1', u'pressure_trend': u'0', u'visibility_mi': u'10.0', u'wind_string': u'From the NNE at 1.0 MPH Gusting to 4.0 MPH', u'pressure_mb': u'1021', u'temperature_string': u'76.3 F (24.6 C)', u'wind_dir': u'NNE', u'icon': u'partlycloudy', u'wind_degrees': 13, u'precip_1hr_in': u'0.00', u'local_tz_offset': u'-0500', u'wind_kph': 1.6, u'wind_gust_mph': u'4.0', u'observation_time': u'Last Updated on September 15, 10:23 AM CDT', u'UV': u'5', u'heat_index_string': u'NA', u'observation_epoch': u'1410794625', u'precip_1hr_metric': u' 0', u'relative_humidity': u'100%', u'observation_time_rfc822': u'Mon, 15 Sep 2014 10:23:45 -0500', u'precip_1hr_string': u'0.00 in ( 0 mm)', u'feelslike_string': u'76.3 F (24.6 C)', u'history_url': u'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=KTXROCKW1'}, u'response': {u'termsofService': u'http://www.wunderground.com/weather/api/d/terms.html', u'version': u'0.1', u'features': {u'conditions': 1}}}
    return r.json()


def parse_citystate(citystate):
    citystate_split = citystate.split(',')
    city = citystate_split[0].replace(' ', '_')
    state = citystate_split[1].strip()

    return (city, state)


def parse_weather(weather_json):
    wdict = weather_json['current_observation']

    wants_formatted = {}
    wants = [
        'UV', 'dewpoint_c', 'dewpoint_f', 'feelslike_c', 'feelslike_f',
        'heat_index_c', 'heat_index_f', 'nowcast', 'observation_time_rfc822', 'precip_1hr_in',
        'precip_1hr_metric', 'precip_today_in', 'precip_today_metric', 'pressure_in', 'pressure_mb',
        'pressure_trend', 'relative_humidity', 'temp_c', 'temp_f', 'visibility_km', 'visibility_mi',
        'weather', 'wind_degrees', 'wind_dir', 'wind_gust_kph', 'wind_gust_mph',
        'wind_kph', 'wind_mph', 'wind_string', 'windchill_c', 'windchill_f',
        'windchill_string'
    ]
    for key, value in wdict.iteritems():
        if key in wants:
            if key == 'observation_time_rfc822':
                key = 'observation_time'
                value = rfc822.parsedate_tz(value)
                value = datetime.datetime(value[0], value[1], value[2], value[3], value[4], value[5]).strftime('%Y-%m-%d %H:%M:%S')
            if value == 'NA': value = None
            if key == 'nowcast': value = value.replace('\n', ' ').strip()
            wants_formatted[str(key)] = value

    return wants_formatted


def save_weather(weather):
    connection = MySQLdb.connect(config.opts['mysql']['host'], config.opts['mysql']['username'], config.opts['mysql']['password'], config.opts['mysql']['database'])
    cursor = connection.cursor()

    query = 'INSERT INTO weather(\
                uv, dewpoint_c, dewpoint_f, feelslike_c, feelslike_f,\
                heat_index_c, heat_index_f, nowcast, observation_time, precip_1hr_in, \
                precip_1hr_metric, precip_today_in, precip_today_metric, pressure_in, pressure_mb,\
                pressure_trend, relative_humidity, temp_c, temp_f, visibility_km,\
                visibility_mi, weather, wind_degrees, wind_dir, wind_gust_kph,\
                wind_gust_mph, wind_kph, wind_mph, wind_string, windchill_c,\
                windchill_f, windchill_string\
            )\
            VALUES(\
                %s, %s, %s, %s, %s,\
                %s, %s, %s, %s, %s,\
                %s, %s, %s, %s, %s,\
                %s, %s, %s, %s, %s,\
                %s, %s, %s, %s, %s,\
                %s, %s, %s, %s, %s,\
                %s, %s\
            )'
    cursor.execute(query, (
        weather['UV'], weather['dewpoint_c'], weather['dewpoint_f'], weather['feelslike_c'], weather['feelslike_f'],
        weather['heat_index_c'], weather['heat_index_f'], weather['nowcast'], weather['observation_time'], weather['precip_1hr_in'],
        weather['precip_1hr_metric'], weather['precip_today_in'], weather['precip_today_metric'], weather['pressure_in'], weather['pressure_mb'],
        weather['pressure_trend'], weather['relative_humidity'], weather['temp_c'], weather['temp_f'], weather['visibility_km'],
        weather['visibility_mi'], weather['weather'], weather['wind_degrees'], weather['wind_dir'], weather['wind_gust_kph'],
        weather['wind_gust_mph'], weather['wind_kph'], weather['wind_mph'], weather['wind_string'], weather['windchill_c'],
        weather['windchill_f'], weather['windchill_string']
    ))

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    sys.exit(main())
