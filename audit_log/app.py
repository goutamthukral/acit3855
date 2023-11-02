import connexion
import yaml
import logging
import logging.config
import datetime
import connexion
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

from connexion import NoContent
from flask_cors import CORS, cross_origin
# from base import Base
# from record_temperature import Temperature
# from record_weather import Weather



with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

user = app_config['datastore']['user']
password = app_config['datastore']['password']
hostname = app_config['datastore']['hostname']
port = app_config['datastore']['port']
db = app_config['datastore']['db']

logger.info(f"Connecting to DB. Hostname: {hostname}, Port: {port}")


def get_temperature_reading(index):

    """ Gets temperature readings after the timestamp """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                            app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving temperature recording at index %d" % index)
    current_index = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg['type'] == "temperature":
                if current_index == index:
                    return msg["payload"], 200
                current_index = current_index + 1

            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
    except:
        logger.error("No more messages found")

    logger.error("Could not find temperature at index %d" % index)
    return { "message": "Not Found"}, 404


def get_weather_recording(index):

    """ Gets weather recordings after the timestamp """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                            app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving weather condition recording at index %d" % index)
    current_index = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg['type'] == "weather_condition":
                if current_index == index:
                    return msg["payload"], 200
                current_index = current_index + 1

            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200

    except:
        logger.error("No more messages found")

    logger.error("Could not find weather condition recording at index %d" % index)
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

app.add_api("openapi.yml",
strict_validation=True,
validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110, host="0.0.0.0")

