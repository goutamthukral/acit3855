import uuid
import connexion
import threading 
import requests
import yaml
import logging
import logging.config
import datetime
import json
import time
from pykafka import KafkaClient
import os

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

# with open('app_conf.yml', 'r') as f:
#     app_config = yaml.safe_load(f.read())

# with open('log_conf.yml', 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

# logger = logging.getLogger('basicLogger')

kafka_server = app_config['events']['hostname']
kafka_port = app_config['events']['port']
kafka_topic = app_config['events']['topic']

max_retries = app_config['kafka']['max_retries']  # Maximum number of retries
current_retry_count = 0

while current_retry_count < max_retries:
    try:
        logger.info(f"Trying to connect to Kafka. Retry count: {current_retry_count}")
        client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
        topic = client.topics[str.encode("events")]
        logger.info("Connection to Kafka successful.")
        break 
    except Exception as e:
        logger.error(f"Connection to Kafka failed: {str(e)}")
        if current_retry_count < max_retries:  
            sleep_time = app_config['kafka']['sleep_time']  
            logger.info(f"Retrying connection after {sleep_time} seconds.")
            time.sleep(sleep_time)
            current_retry_count += 1
        else:
            logger.error("Maximum retries reached")

producer = topic.get_sync_producer()

from connexion import NoContent
MAX_EVENTS = 10
EVENT_FILE = "events.json"
lock = threading.Lock()

def record_temperature_reading(body):
    """ Receives a temperature reading """

    trace_id = uuid.uuid4()
    type_object = "temperature"   
    logger.info(f"Received event {type_object} recording with a trace id of {trace_id}")
    body['trace_id'] = str(trace_id)

    msg = { "type": type_object,
            "datetime" :
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned event {type_object} recording response {trace_id} with status 201")

    return NoContent, 201

def record_weather_condition(body):

    trace_id = uuid.uuid4()
    type_object = "weather_condition"   
    logger.info(f"Received event {type_object} recording with a trace id of {trace_id}")
    body['trace_id'] = str(trace_id)

    msg = { "type": type_object,
            "datetime" :
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned event {type_object} recording response {trace_id} with status 201")

    return NoContent, 201

def get_health():
    return 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path="/receiver",
strict_validation=True,
validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
