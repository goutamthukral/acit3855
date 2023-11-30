import connexion
import yaml
import logging
import logging.config
import datetime
import connexion
import json
import requests
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin


if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

# with open('log_conf.yml', 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

# logger = logging.getLogger('basicLogger')

# with open('app_conf.yml', 'r') as f:
#     app_config = yaml.safe_load(f.read())


def populate_stats():
    
    logger.info("Periodic Processing started")
    filename = app_config['datastore']['filename']
    url1 = app_config['eventstore']['url1']
    url2 = app_config['eventstore']['url2']

    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
    else:
        data = {
            "num_temperature_readings": 0,
            "avg_max_temperature_reading": 0,
            "num_weather_recordings": 0,
            "max_humidity_reading": 0,
            "last_updated": 0
        }

    num_temperature_readings = data['num_temperature_readings']
    avg_max_temperature_reading = data['avg_max_temperature_reading']
    num_weather_recordings = data['num_weather_recordings']
    max_humidity_reading = data['max_humidity_reading']
    last_updated = data['last_updated']


    if (last_updated == 0):
        current_datetime = datetime.datetime.now()
        current_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        last_updated = current_datetime
    
    current_timestamp = datetime.datetime.now()
    current_timestamp = current_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    response1 = requests.get(url1+ "?start_timestamp=" + last_updated + "&end_timestamp=" + current_timestamp)
    response2 = requests.get(url2+ "?start_timestamp=" + last_updated + "&end_timestamp=" + current_timestamp)

    if response1.status_code != 200 or response2.status_code != 200:
        logger.error("ERROR")

    if response1.status_code == 200 and response2.status_code == 200:
            
        temperature_data = response1.json()
        weather_data = response2.json()


        old_num_temperature_readings = num_temperature_readings
        new_temperature_readings = len(temperature_data)
        num_temperature_readings = num_temperature_readings + new_temperature_readings


        new_weather_recordings = len(weather_data)
        num_weather_recordings = num_weather_recordings + new_weather_recordings

        sum_temperature = 0

        for element in temperature_data:
            sum_temperature = sum_temperature + element['maximum_temperature']

        avg_max_temperature_reading = int((avg_max_temperature_reading*old_num_temperature_readings + sum_temperature)/(num_temperature_readings+1)) 

        for element in weather_data:
            if element['humidity'] > max_humidity_reading:
                max_humidity_reading = element['humidity']
        
        # current_datetime = datetime.datetime.now()
        # current_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        last_updated = current_timestamp

        data = {
                "num_temperature_readings": num_temperature_readings,
                "avg_max_temperature_reading": avg_max_temperature_reading,
                "num_weather_recordings": num_weather_recordings,
                "max_humidity_reading": max_humidity_reading,
                "last_updated": last_updated
                }
        
        with open(filename, "w") as json_file:
            json.dump(data, json_file)
            
        logger.info(f"Number of events received for temperature recording {new_temperature_readings}")
        logger.info(f"Number of events received for weather recording {new_weather_recordings}")        

    if response1.status_code == 500 or response2.status_code == 500:
        print("ERROR RESPONSE")

    logger.debug(f"The number of temperature readings are {num_temperature_readings}, "
                    f"the average maximum temperature is {avg_max_temperature_reading}, "
                    f"the number of weather readings are {num_weather_recordings}, "
                    f"the maximum humidity reading is {max_humidity_reading}")

    logger.info("Periodic Processing ended")

def get_health():
    return 200

def get_stats():

    logger.info("The request has started")
    filename = app_config['datastore']['filename']
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        
        num_temperature_readings = data['num_temperature_readings']
        avg_max_temperature_reading = data['avg_max_temperature_reading']
        num_weather_recordings =  data['num_weather_recordings']
        max_humidity_reading = data['max_humidity_reading']
    
        logger.debug(f"The number of temperature readings are {num_temperature_readings}, "
                     f"the average maximum temperature is {avg_max_temperature_reading}, "
                     f"the number of weather readings are {num_weather_recordings}, "
                     f"the maximum humidity reading is {max_humidity_reading}")
        
        logger.info("Request has been completed")
        return data, 200
                     
    else:
        logger.error("Statistics do not exist")
        return "Statistics do not exist", 404


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                    'interval',
                    seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

app.add_api("openapi.yml", base_path="/processing",
strict_validation=True,
validate_responses=True)

if __name__ == "__main__":
# run our standalone gevent server
    init_scheduler()
    app.run(port=8100, host="0.0.0.0", use_reloader=False)
