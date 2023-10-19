from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Temperature(Base):
    """ Temperature """

    __tablename__ = "temperature_recording"

    id = Column(Integer, primary_key=True)
    trace_id = Column(String(250), nullable=False)
    record_id = Column(String(250), nullable=False)
    location = Column(String(250), nullable=False)
    maximum_temperature = Column(Integer, nullable=False)
    minimum_temperature = Column(Integer, nullable=False) 
    date = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, trace_id, record_id, location, maximum_temperature, minimum_temperature, date):
        """ Initializes a temperature reading """
        self.trace_id = trace_id
        self.record_id = record_id
        self.location = location
        self.date = date
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.maximum_temperature = maximum_temperature
        self.minimum_temperature = minimum_temperature

    def to_dict(self):
        """ Dictionary Representation of a temperature reading """
        dict = {}
        dict['id'] = self.id
        dict['trace_id'] = self.trace_id
        dict['record_id'] = self.record_id
        dict['location'] = self.location
        dict['maximum_temperature'] = self.maximum_temperature
        dict['minimum_temperature'] = self.minimum_temperature
        dict['date_created'] = self.date_created
        dict['date'] = self.date

        return dict
