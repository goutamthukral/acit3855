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

def populate_stats():
    filename = app_config['datastore']['filename']
    receiver_endpoint = app_config['eventstore']['receiver']
    storage_endpoint = app_config['eventstore']['storage']
    processing_endpoint = app_config['eventstore']['processing']
    audit_endpoint = app_config['eventstore']['audit']

    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
    else:
        data = {
            "receiver": "Down",
            "storage": "Down",
            "processing": "Down",
            "audit": "Down",
            "last_updated": 0
        }

    if (last_updated == 0):
        current_datetime = datetime.datetime.now()
        current_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        last_updated = current_datetime
    
    current_timestamp = datetime.datetime.now()
    current_timestamp = current_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    receiver_health = requests.get(receiver_endpoint)
    storage_health = requests.get(storage_endpoint)
    processing_health = requests.get(processing_endpoint)
    audit_health = requests.get(audit_endpoint)

    if receiver_health.status_code == 200:
        data['receiver'] = "Running"
    else:
        data['receiver'] = "Down"        

    if storage_health.status_code == 200:
        data['storage'] = "Running"
    else:
        data['storage'] = "Down"   

    if processing_health.status_code == 200:
        data['processing'] = "Running"
    else:
        data['processing'] = "Down"  

    if audit_health.status_code == 200:
        data['audit'] = "Running"
    else:
        data['audit'] = "Down"  

    current_datetime = datetime.datetime.now()
    current_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    data['last_updated'] = current_timestamp

    with open(filename, "w") as json_file:
        json.dump(data, json_file)
            
    logger.info(f"Status service logged") 

    logger.info("Periodic Processing ended")

def get_health():

    logger.info("The request has started")
    filename = app_config['datastore']['filename']
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
          
        logger.info("Request has been completed")
        return data, 200
                     
    else:
        logger.error("Health statistics do not exist")
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
    app.run(port=8120, host="0.0.0.0", use_reloader=False)
