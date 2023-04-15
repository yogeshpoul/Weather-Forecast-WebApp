from flask import Flask, render_template, request, abort
import json
import urllib.request
import datetime

app = Flask(__name__)

def to_celsius(temp):
    return round(float(temp) - 273.15, 2)

@app.route('/', methods=['POST', 'GET'])
def weather():
    api_key = '48a90ac42caa09f90dcaeee4096b9e53'
    if request.method == 'POST':
        city = request.form['city']
    else:
        city = 'parbhani'

    # Current weather
    try:
        current_source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q=' + city + '&appid=' + api_key).read()
        current_data = json.loads(current_source)
        current_temp = to_celsius(current_data['main']['temp'])
        current_desc = current_data['weather'][0]['description']
    except:
        return abort(404)

    # Historical weather
    past_data = []
    for i in range(1, 2):
        past_date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        try:
            past_source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q=' + city + '&appid=' + api_key + '&dt=' + past_date).read()
            past_data.append({
                "date": past_date,
                "temperature": to_celsius(json.loads(past_source)['main']['temp']),
                "description": json.loads(past_source)['weather'][0]['description']
            })
        except Exception as e:
            past_data.append({
            "date": past_date,
            "temperature": None,
            "description": f"No data available for {past_date}: {e}"
        })

    # Forecast weather
    try:
        forecast_source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast?q=' + city + '&appid=' + api_key).read()
        forecast_data = json.loads(forecast_source)
    except:
        return abort(404)

    # data for the variable list_of_data
    data = {
        "cityname": str(city),
        "country_code": str(forecast_data['city']['country']),
        "today": datetime.datetime.now().strftime('%Y-%m-%d'),
        "current_temp": current_temp,
        "current_desc": current_desc,
        "past": past_data,
        "forecast": [],
        "future": []
    }

    for forecast in forecast_data['list']:
        date_time_str = forecast['dt_txt']
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

        if date_time_obj.strftime('%H:%M:%S') == '12:00:00':
            if date_time_obj.date() > datetime.datetime.now().date():
                data['future'].append({
                    "date": date_time_obj.strftime('%Y-%m-%d'),
                    "temperature": to_celsius(forecast['main']['temp']),
                    "description": forecast['weather'][0]['description']
                })
            else:
                data['forecast'].append({
                    "date": date_time_obj.strftime('%Y-%m-%d'),
                    "temperature": to_celsius(forecast['main']['temp']),
                    "description": forecast['weather'][0]['description']
                })

    data['past'] = sorted(data['past'], key=lambda x: x['date'])
    data['forecast'] = sorted(data['forecast'], key=lambda x: x['date'])
    data['future'] = sorted(data['future'], key=lambda x: x['date'])

    return render_template('weather.html', data=data)



if __name__ == '__main__':
    app.run(debug=True)
