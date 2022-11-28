# Written by Zach Keeler, Raymond Bicknell, and Heidi Lamb for CS370 at CSU in Fall 2022

import csv
import argparse
import Adafruit_DHT as ada
from statistics import fmean
from socket import socket, AF_INET, SOCK_DGRAM
from datetime import datetime

# command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('ip_address', help='ip address of the server that receives the messages', type=str)
parser.add_argument('-a', '--average', help='number of sensor readings to average together', type=int, default=6, nargs='?', const=1)
parser.add_argument('-l', '--log_file', help='location of logging file', type=str, default='log.csv', nargs='?', const=1)
parser.add_argument('-hmin', '--hum_min', help='minimum humidity in percent', type=float, default=40, nargs='?', const=1)
parser.add_argument('-hmax', '--hum_max', help='maximum humidity in percent', type=float, default=50, nargs='?', const=1)
parser.add_argument('-hdev', '--hum_dev', help='allowable humidity deviation before alerting', type=float, default=5, nargs='?', const=1)
parser.add_argument('-tmin', '--temp_min', help='minimum temperature in celcius', type=float, default=20.0, nargs='?', const=1)
parser.add_argument('-tmax', '--temp_max', help='maximum temperature in celcius', type=float, default=24.0, nargs='?', const=1)
parser.add_argument('-tdev', '--temp_dev', help='allowable temperature deviation before alerting', type=float, default=2, nargs='?', const=1)
args = parser.parse_args()

# GPIO pins for the two DHT11 temperature and humidity sensors
DHT_SENSOR = ada.DHT11
INSIDE_DHT_PIN = 4
OUTSIDE_DHT_PIN = 24

# socket settings for connecting to server
SERVER_IP   = args.ip_address
PORT_NUMBER = 5000
mySocket = socket( AF_INET, SOCK_DGRAM )

# appends values to the end of a csv file specified in the arguments
def write_csv(in_hum, in_temp, out_hum, out_temp):
    file = open(args.log_file, 'a', newline='')
    writer = csv.writer(file)    
    writer.writerow([in_hum, in_temp, out_hum, out_temp, datetime.now()])  
    file.close()

# returns the appropriate message to send to the laptop
# for example, if the inside temperature is higher than the temperature max, and the outside temperature 
# is lower than the inside temperature by at least the temperature deviation, then open the window
def get_message(in_hum, in_temp, out_hum, out_temp):
    if in_temp < args.temp_min and out_temp >= (in_temp + args.temp_dev):
        return "It is too cold inside, open the window"
    elif in_temp > args.temp_max and out_temp <= (in_temp - args.temp_dev):
        return "It is too hot inside, open the window"
    elif in_hum < args.hum_min and out_hum >= (in_hum + args.hum_dev):
        return "It is too dry inside, open the window"
    elif in_hum > args.hum_max and out_hum <= (in_hum - args.hum_dev):
        return "It is too humid inside, open the window"
    return "Current inside temp and humidity is good, close the window."
    
if __name__ == "__main__":
    while True:
        in_hum_lst = []
        in_temp_lst = []
        out_hum_lst = []
        out_temp_lst = []

        for i in range(args.average):
            # read the humidity and temperature from the sensor
            in_hum, in_temp = ada.read_retry(DHT_SENSOR, INSIDE_DHT_PIN)
            out_hum, out_temp = ada.read_retry(DHT_SENSOR, OUTSIDE_DHT_PIN)

            # store in corresponding lists
            in_hum_lst.append(in_hum)
            in_temp_lst.append(in_temp)
            out_hum_lst.append(out_hum)
            out_temp_lst.append(out_temp)

        # average the lists
        avg_in_hum = fmean(in_hum_lst)
        avg_in_temp = fmean(in_temp_lst)
        avg_out_hum = fmean(out_hum_lst)
        avg_out_temp = fmean(out_temp_lst)

        # log readings to csv
        write_csv(avg_in_hum, avg_in_temp, avg_out_hum, avg_out_temp)

        # get appropriate message for instructions on opening or closing the window
        message = get_message(avg_in_hum, avg_in_temp, avg_out_hum, avg_out_temp)
        print("values are:", avg_in_hum, avg_in_temp, avg_out_hum, avg_out_temp, datetime.now(), "message is:", message)
        mySocket.sendto(message.encode('utf-8'),(SERVER_IP,PORT_NUMBER))