import uuid
import connexion
import threading 
import requests
import yaml
import logging
import logging.config
import datetime
import json
from pykafka import KafkaClient

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

from connexion import NoContent
MAX_EVENTS = 10
EVENT_FILE = "events.json"
lock = threading.Lock()

def record_temperature_reading(body):
    """ Receives a temperature reading """

    # with lock:

    trace_id = uuid.uuid4()

    type_object = "temperature"   

    kafka_server = app_config['events']['hostname']
    kafka_port = app_config['events']['port']
    kafka_topic = app_config['events']['topic']
    logger.info(f"Received event {type_object} recording with a trace id of {trace_id}")

    headers = {'Content-Type': 'application/json'}
    body['trace_id'] = str(trace_id)

    # response = requests.post(url_path, json=body, headers=headers)

    client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
    topic = client.topics[str.encode(kafka_topic)]
    producer = topic.get_sync_producer()
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
    # with lock:

    trace_id = uuid.uuid4()

    type_object = "weather_condition"   

    kafka_server = app_config['events']['hostname']
    kafka_port = app_config['events']['port']
    kafka_topic = app_config['events']['topic']
    logger.info(f"Received event {type_object} recording with a trace id of {trace_id}")

    body['trace_id'] = str(trace_id)

    # response = requests.post(url_path, json=body, headers=headers)

    client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
    topic = client.topics[str.encode(kafka_topic)]
    producer = topic.get_sync_producer()
    msg = { "type": type_object,
            "datetime" :
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned event {type_object} recording response {trace_id} with status 201")

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml",
strict_validation=True,
validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
