import telebot, feedparser, re, json, urllib.request
from datetime import datetime
from yr.libyr import Yr
from settings import AWAPIKEY, LAT, LNG, RP5CITY, LANGRP5, AWCITY, LANGAW, YRCITY, TERMOMETER_IP
from utils import cleanhtml
from lib import (pollen_translate, 
                 forecast_icons, 
                 severity_icons, 
                 accuweather_sticker, 
                 wind_direction_arrow)


class YrNow(object):
    def __init__(self, city):
        self.weather = Yr(location_name=city)
        self.now = self.weather.now()
        self.symbol = self.now['symbol']['@var']
        self.precipitation = self.now['precipitation']['@value']
        self.windDirection = self.now['windDirection']['@code']
        self.windSpeed = self.now['windSpeed']['@mps']
        self.temperature = self.now['temperature']['@value']
        self.pressure = self.now['pressure']['@value']
        if self.windDirection in wind_direction_arrow.keys():
            self.wind_direction_arrow_icon = wind_direction_arrow[self.windDirection]
        else:
            self.wind_direction_arrow_icon = ''

    def __str__(self):
        return f"Сейчас 🌡 {self.temperature}°C, Давление {self.pressure}, ☂️ {self.precipitation}мм, "\
               f"🌬 {self.wind_direction_arrow_icon} {self.windSpeed}м/с\n\n"

    
def get_rp5_weather_summary(city, lang):
    rp5_url = "http://rp5.ua/rss/" + city + "/" + lang
    rp5_data = feedparser.parse(rp5_url)
    last_rp5 = rp5_data.entries[0]
    return f"{last_rp5['title'][:8]} {cleanhtml(last_rp5['summary'])}\n"


def get_own_measure():
    url = f"http://{TERMOMETER_IP}/"
    try:
        with urllib.request.urlopen(url) as aw_url:
            data = json.loads(aw_url.read().decode())
            return f"\nСобственные измерения: {data['temperature']}°C, Влажность {data['humidity']}%, "\
                f"Давление {data['pressure']} мм рс"
    except:
        return ''


class Accuweather(object):
    url_first_part = "http://dataservice.accuweather.com/forecasts/v1/daily/1day/"
    url_api = '?apikey='
    url_lang = "&language="
    url_fin_part = "&details=true&metric=true"

    def __init__(self, city, apikey, lang):
        self.url = self.url_first_part + city + self.url_api + apikey 
        self.url += self.url_lang + lang + self.url_fin_part
        with urllib.request.urlopen(self.url) as self.aw_url:
            self.data = json.loads(self.aw_url.read().decode())
            self.last_update = datetime.now()
        

    def refresh(self):
        if (datetime.now() - self.last_update).seconds > 1800:
            with urllib.request.urlopen(self.url) as self.aw_url:
                self.data = json.loads(self.aw_url.read().decode())
                self.last_update = datetime.now()

    @property
    def headline(self):
        try:
            part = self.data['Headline']
            text = part['Text']
            date = datetime.fromtimestamp(part['EffectiveEpochDate']).strftime('%d/%m/%Y %H:%M')
            end_date = datetime.fromtimestamp(part['EndEpochDate']).strftime('%d/%m/%Y %H:%M')
            category = part['Category']
            severity = part['Severity']

            if category in forecast_icons.keys():
                category_icon = forecast_icons[category]
            else:
                category_icon = category

            return f"{severity_icons[severity]} {category_icon} {text} ({date} - {end_date})"
        except:
            return ''
    
    @property
    def air(self):
        part = self.data['DailyForecasts'][0]['AirAndPollen']
        air_q = part[0]['Category']
        air_q_value = part[0]['Value']
        air_q_type = part[0]['Type']
        air_string = f' Качество воздуха: {air_q} ({air_q_value} {air_q_type})'
        for i in part[1:]:
            if i['Value']:
                air_string += f" {pollen_translate[i['Name']]}: {i['Category']} ({i['Value']})\n"
        return air_string

    @property
    def temperature(self):
        part = self.data['DailyForecasts'][0]['Temperature']
        minimal = part['Minimum']['Value']
        maximal = part['Maximum']['Value']
        return f"\n🌡 {minimal}°C...{maximal}°C"

    @property
    def real_feel_temperature_shade(self):
        part = self.data['DailyForecasts'][0]['RealFeelTemperatureShade']
        minimal = part['Minimum']['Value']
        maximal = part['Maximum']['Value']
        return f"🌡 в тени ощущается как: {minimal}°C...{maximal}°C"

    @property
    def real_feel_temperature(self):
        part = self.data['DailyForecasts'][0]['RealFeelTemperature']
        minimal = part['Minimum']['Value']
        maximal = part['Maximum']['Value']
        return f"ощущается {minimal}°C...{maximal}°C"
    
    @property
    def hours_of_sun(self):
        return self.data['DailyForecasts'][0]['HoursOfSun']

    @property
    def sun(self):
        part =self.data['DailyForecasts'][0]['Sun']
        sunrise = datetime.fromtimestamp(part['EpochRise']).strftime('%H:%M')
        sunset = datetime.fromtimestamp(part['EpochSet']).strftime('%H:%M')
        return f"☀️ Рассвет: {sunrise} Закат: {sunset} {self.hours_of_sun} часов солнца"

    @property
    def moon(self):
        part =self.data['DailyForecasts'][0]['Moon']
        moonrise = datetime.fromtimestamp(part['EpochRise']).strftime('%H:%M')
        moonset = datetime.fromtimestamp(part['EpochSet']).strftime('%H:%M')
        return f"🌕 Восход луны: {moonrise} Закат луны: {moonset}"
        
    @property
    def day(self):
        part = self.data['DailyForecasts'][0]['Day']
        icon_number = part['Icon']
        icon_phrase = part['LongPhrase']
        precipitation_probability = part['PrecipitationProbability']
        thunderstorm_probability = part['ThunderstormProbability']
        rain_probability = part['RainProbability']
        snow_probability = part['SnowProbability']
        ice_probability = part['IceProbability']
        wind_direction_text = part['Wind']['Direction']['Localized']
        wind_direction_text_en = part['Wind']['Direction']['English']
        wind_direction_degrees = part['Wind']['Direction']['Degrees']
        wind_speed = part['Wind']['Speed']['Value']
        wind_gust_direction_text= part['WindGust']['Direction']['Localized']
        wind_gust_direction_text_en = part['WindGust']['Direction']['English']
        wind_gust_direction_degrees = part['WindGust']['Direction']['Degrees']
        wind_gust_speed = part['WindGust']['Speed']['Value'] 
        total_liquid = part['TotalLiquid']['Value']
        rain = part['Rain']['Value']
        hours_of_rain = part['HoursOfRain']
        snow = part['Snow']['Value']
        hours_of_snow = part['HoursOfSnow']
        ice = part['Ice']['Value']
        hours_of_ice = part['HoursOfIce']
        cloud_cover = part['CloudCover']
        
        if part['HasPrecipitation']: 
            precipitation = 'осадки'
        else: 
            precipitation = 'без осадков'       

        if wind_direction_text_en in wind_direction_arrow.keys():
            wind_direction_arrow_icon = wind_direction_arrow[wind_direction_text_en]
        else:
            wind_direction_arrow_icon = ''

        if wind_gust_direction_text_en in wind_direction_arrow.keys():
            wind_gust_direction_arrow_icon = wind_direction_arrow[wind_gust_direction_text_en]
        else:
            wind_gust_direction_arrow_icon = ''

        result = f"{icon_phrase}, {precipitation}.\n"
        result += f"Ветер {wind_direction_text} {wind_direction_arrow_icon}"
        result += f"{wind_speed}км/ч"
        result += f", порывы {wind_gust_direction_text} {wind_gust_direction_arrow_icon}" 
        result += f" до {wind_gust_speed}км/ч\n"
        result += f"Облачный покров: {cloud_cover} % \n"
        result += f"вероятность осадков {precipitation_probability}%"

        if thunderstorm_probability:
            result += f", гроза {thunderstorm_probability}%"
        if rain_probability:
            result += f", дождь {rain_probability}% ({hours_of_rain}час.)"
        if snow_probability:
            result += f", снег {snow_probability}% ({hours_of_snow}час.)"
        if ice_probability:
            result += f", лед {ice_probability}%"
        if total_liquid:
            result += f". Всего: {total_liquid}мм \n"
        # if rain:
        #     result += f" Дождь: {rain} мм  {hours_of_rain}час. \n"
        # if snow:
        #     result += f" Снег: {snow} мм  {hours_of_snow} час. \n"
        # if ice:
        #     result += f" Лед: {ice} мм  {hours_of_ice} час. \n"
        return result

    @property
    def night(self):
        part = self.data['DailyForecasts'][0]['Night']
        icon_number = part['Icon']
        icon_phrase = part['LongPhrase']
        precipitation_probability = part['PrecipitationProbability']
        thunderstorm_probability = part['ThunderstormProbability']
        rain_probability = part['RainProbability']
        snow_probability = part['SnowProbability']
        ice_probability = part['IceProbability']
        wind_direction_text = part['Wind']['Direction']['Localized']
        wind_direction_text_en = part['Wind']['Direction']['English']
        wind_direction_degrees = part['Wind']['Direction']['Degrees']
        wind_speed = part['Wind']['Speed']['Value']
        wind_gust_direction_text= part['WindGust']['Direction']['Localized']
        wind_gust_direction_text_en = part['WindGust']['Direction']['English']
        wind_gust_direction_degrees = part['WindGust']['Direction']['Degrees']
        wind_gust_speed = part['WindGust']['Speed']['Value'] 
        total_liquid = part['TotalLiquid']['Value']
        rain = part['Rain']['Value']
        hours_of_rain = part['HoursOfRain']
        snow = part['Snow']['Value']
        hours_of_snow = part['HoursOfSnow']
        ice = part['Ice']['Value']
        hours_of_ice = part['HoursOfIce']
        cloud_cover = part['CloudCover']
        
        if part['HasPrecipitation']: 
            precipitation = 'осадки'
        else: 
            precipitation = 'без осадков'       

        if wind_direction_text_en in wind_direction_arrow.keys():
            wind_direction_arrow_icon = wind_direction_arrow[wind_direction_text_en]
        else:
            wind_direction_arrow_icon = ''

        if wind_gust_direction_text_en in wind_direction_arrow.keys():
            wind_gust_direction_arrow_icon = wind_direction_arrow[wind_gust_direction_text_en]
        else:
            wind_gust_direction_arrow_icon = ''

        result = f"{icon_phrase}, {precipitation}. "
        result += f"Ветер {wind_direction_text} {wind_direction_arrow_icon}"
        result += f"{wind_speed}км/ч"
        result += f", порывы {wind_gust_direction_text} {wind_gust_direction_arrow_icon}" 
        result += f" до {wind_gust_speed}км/ч\n"
        result += f"Облачный покров: {cloud_cover} % \n"
        result += f"вероятность осадков {precipitation_probability}%"

        if thunderstorm_probability:
            result += f", гроза {thunderstorm_probability}%"
        if rain_probability:
            result += f", дождь {rain_probability}% ({hours_of_rain}час.)"
        if snow_probability:
            result += f", снег {snow_probability}% ({hours_of_snow} час.)"
        if ice_probability:
            result += f", лед {ice_probability}%"
        if total_liquid:
            result += f". Всего: {total_liquid}мм \n"
        # if rain:
        #     result += f" Дождь: {rain} мм  {hours_of_rain}час. \n"
        # if snow:
        #     result += f" Снег: {snow} мм  {hours_of_snow} час. \n"
        # if ice:
        #     result += f" Лед: {ice} мм  {hours_of_ice} час. \n"
        return result

    def __str__(self):
        return f"{self.headline}\n{self.temperature}, {self.real_feel_temperature}\n\n"\
               f"День: {self.day}\n"\
               f"Ночь: {self.night}" 


if __name__ == '__main__':
    now = YrNow(YRCITY)
    forecast = Accuweather(AWCITY, AWAPIKEY, LANGAW)
    print(get_rp5_weather_summary(RP5CITY, LANGRP5))
    print(forecast)
    print(now)
    print(get_own_measure())
