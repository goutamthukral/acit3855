from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Weather(Base):
    """ Weather Recording """

    __tablename__ = "weather_recording"

    id = Column(Integer, primary_key=True)
    trace_id = Column(String(250), nullable=False)
    record_id = Column(String(250), nullable=False)
    location = Column(String(250), nullable=False)
    wind_speed = Column(Integer, nullable=False)
    humidity = Column(Integer, nullable=False) 
    weather_condition = Column(String(100), nullable=False) 
    date = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, trace_id, record_id, location, wind_speed, humidity, weather_condition, date):
        """ Initializes a weather condition reading """
        self.trace_id = trace_id
        self.record_id = record_id
        self.location = location
        self.date = date
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.wind_speed = wind_speed
        self.humidity = humidity
        self.weather_condition = weather_condition

    def to_dict(self):
        """ Dictionary Representation of a weather condition reading """
        dict = {}
        dict['id'] = self.id
        dict['trace_id'] = self.trace_id
        dict['record_id'] = self.record_id
        dict['location'] = self.location
        dict['wind_speed'] = self.wind_speed
        dict['humidity'] = self.humidity
        dict['weather_condition'] = self.weather_condition        
        dict['date_created'] = self.date_created
        dict['date'] = self.date

        return dict
