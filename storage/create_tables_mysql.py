import mysql
import mysql.connector
db_conn = mysql.connector.connect(host="acit3855.westus.cloudapp.azure.com", user="user",
password="password", database="events")
db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE temperature_recording
          (id INT NOT NULL AUTO_INCREMENT, 
           trace_id VARCHAR(250) NOT NULL,  
           record_id VARCHAR(250) NOT NULL,
           location VARCHAR(250) NOT NULL,
           maximum_temperature INTEGER NOT NULL,
           minimum_temperature INTEGER NOT NULL,
           date VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT temperature_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE weather_recording
          (id INT NOT NULL AUTO_INCREMENT, 
           trace_id VARCHAR(250) NOT NULL,
           record_id VARCHAR(250) NOT NULL,
           location VARCHAR(250) NOT NULL,
           wind_speed INTEGER NOT NULL,
           humidity INTEGER NOT NULL,
           weather_condition VARCHAR(100) NOT NULL,
           date VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT weather_recording_pk PRIMARY KEY (id))
          ''')
db_conn.commit()
db_conn.close()