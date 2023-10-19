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
from base import Base
from record_temperature import Temperature
from record_weather import Weather
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



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

DB_ENGINE = create_engine(f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}')

logger.info(f"Connecting to DB. Hostname: {hostname}, Port: {port}")

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

# def record_temperature_reading(body):
#     """ Receives a temperature reading """

#     session = DB_SESSION()

#     temp = Temperature(body['trace_id'],
#                        body['record_id'],
#                        body['location'],
#                        body['maximum_temperature'],
#                        body['minimum_temperature'],
#                        body['date'])

#     session.add(temp)

#     session.commit()
#     session.close()

#     logger.debug(f"Stored event 'temperature recording' request with a trace id of {body['trace_id']}")

#     return NoContent, 201

# def record_weather_condition(body):
#     """ Receives a weather reading """

#     session = DB_SESSION()

#     wthr = Weather(body['trace_id'],
#                    body['record_id'],
#                    body['location'],
#                    body['wind_speed'],
#                    body['humidity'],
#                    body['weather_condition'],
#                    body['date'])

#     session.add(wthr)

#     session.commit()
#     session.close()

#     logger.debug(f"Stored event 'weather recording' request with a trace id of {body['trace_id']}")

#     return NoContent, 201


def get_temperature_reading(timestamp):

    """ Gets temperature readings after the timestamp """

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    session = DB_SESSION()
    readings = session.query(Temperature).filter(Temperature.date_created >=
                                                    timestamp_datetime).all()

    results_list = []
    for reading in readings:
        element = reading.to_dict()
        element['timestamp'] = element.pop("date_created")
        results_list.append(element)

    session.close()
    logger.info("Query for Temperature readings after %s returns %d results" %(timestamp, len(results_list)))
    return results_list, 200


def get_weather_recording(timestamp):

    """ Gets weather recordings after the timestamp """
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    session = DB_SESSION()
    readings = session.query(Weather).filter(Weather.date_created >=
                                                    timestamp_datetime).all()
    
    results_list = []
    for reading in readings:
        element = reading.to_dict()
        element['timestamp'] = element.pop("date_created")
        results_list.append(element)

    session.close()
    logger.info("Query for Weather recordings after %s returns %d results" %(timestamp, len(results_list)))
    return results_list, 200


def process_messages():

    """ Process event messages """
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}" 
    print(hostname)
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                        reset_offset_on_start=False,
                                        auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:

        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
    
        logger.info("Message: %s" % msg)

        body = msg["payload"]
        
        if msg["type"] == "temperature": # Change this to your event type
            """ Receives a temperature reading """

            session = DB_SESSION()

            temp = Temperature(body['trace_id'],
                            body['record_id'],
                            body['location'],
                            body['maximum_temperature'],
                            body['minimum_temperature'],
                            body['date'])

            session.add(temp)

            session.commit()
            session.close()

            logger.debug(f"Stored event 'temperature recording' request with a trace id of {body['trace_id']}")
        

        elif msg["type"] == "weather_condition": # Change this to your event type
            session = DB_SESSION()
            wthr = Weather(body['trace_id'],
                        body['record_id'],
                        body['location'],
                        body['wind_speed'],
                        body['humidity'],
                        body['weather_condition'],
                        body['date'])

            session.add(wthr)

            session.commit()
            session.close()

            logger.debug(f"Stored event 'weather recording' request with a trace id of {body['trace_id']}")

        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml",
strict_validation=True,
validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()

    app.run(port=8090)

