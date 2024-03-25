import serial
from serial import Serial, SerialException
from serial.tools import list_ports
from datetime import datetime
import pytz
import time
from influxdb import InfluxDBClient
from typing import Optional
from logs import log_init, log


# Constants
ARDUINO_BAUD_RATE       = 115200

INFLUXDB_PORT           = 8086          
INFLUXDB_HOST           = "influxdb"
INFLUXDB_USERNAME       = "admin"   
INFLUXDB_PASSWORD       = "admin"   
INFLUXDB_DATABASE       = "sensor_data"  

DB_WRITE_DELAY          = 60
VALS_TO_IGNORE_THRES    = 200

PAK_TZ = pytz.timezone('Asia/Karachi')

Influx_Client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, username=INFLUXDB_USERNAME, password=INFLUXDB_PASSWORD)

def _detect_arduino_port() -> Optional[str]:
        for port in list_ports.comports():
                if "USB2.0-Ser!" in port.description:
                        return port.device
        return None
                        
def handle_arduino_detection() -> Serial:
        while True:
                try:
                        arduino_port: str = _detect_arduino_port()
                        if arduino_port is None:
                                log.info("Arduino not detected. Retrying in 5 seconds...")
                                time.sleep(5)
                                continue

                        log.info(f"Arduino detect at port {arduino_port}")

                        return serial.Serial(arduino_port, ARDUINO_BAUD_RATE) 

                except SerialException as e:
                        log.error(f"Something went wrong while trying to dynamically detect arduino port: {e}")

                except Exception as e: # need to add proper logging
                        log.critical(f"An unexpected error occurred while trying to dynamically detect arduino port: {e}")
                        time.sleep(0.1)  

def write_to_influxdb(data_dict: dict) -> None:
        json_payload: dict = []

        # convert data_dict to InfluxDB JSON format
        for timestamp, value in data_dict.items():
                json_payload.append({
                                "measurement": "inline_pres", # organizing datasets per sensor (in future more sensors will be added)
                                "tags": {},
                                "time": timestamp,
                                "fields": 
                                {
                                        "value": value
                                }
                        })

        Influx_Client.write_points(json_payload, database=INFLUXDB_DATABASE)

        log.info("Data written to database")

def main():
        last_db_write: float = time.time()
        data_dict: dict = {}  
        Arduino: Serial = None

        log_init(log.DEBUG)

        while True:
                if not Arduino:
                        Arduino = handle_arduino_detection()

                try: 
                        if Arduino.in_waiting > 0:
                                data = int(Arduino.readline().decode().strip())
                                timestamp = datetime.now(PAK_TZ).isoformat()

                                log.debug(f"TimeStamp: {str(timestamp)}, Data: {str(data)}")

                                if data > VALS_TO_IGNORE_THRES: # this check is for ignoring corrupted values, not a proper solution but good enough
                                        data_dict[timestamp] = data

                                current_time = time.time()
                                
                                if current_time - last_db_write >= DB_WRITE_DELAY:
                                        write_to_influxdb(data_dict)
                                        last_db_write = current_time

                                        data_dict.clear()

                except (SerialException, OSError) as e:
                        log.error(f"Something went wrong in the serial stack or arduino was disconnected:{e}")
                        
                        if Arduino:
                                Arduino.close()
                                Arduino = None
                        
                except Exception as e: # add proper logging
                        log.critical(f"An unexpected error occurred while reading arduino serial:{e}") # handle exception properly
                        time.sleep(0.1)  

if __name__ == '__main__':
        main()



