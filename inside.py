import os
import time
import Adafruit_DHT as ada
import pandas
import csv
from datetime import datetime


DHT_SENSOR = ada.DHT11
DHT_PIN = 4

if __name__ == "__main__":
    fields=['humidity','temperature']
    with open(r'cs370logging.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        while True:
            humidity, temperature = ada.read_retry(DHT_SENSOR, DHT_PIN)
            writer.writerow((temperature,humidity,datetime.now()))
            if humidity is not None and temperature is not None:
                print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
            else:
                print("Failed to retrieve data from humidity sensor")


# log inside_temp, outside_temp, inside_humidity, outside_humidity