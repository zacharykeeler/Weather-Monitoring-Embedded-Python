import os
import time
import Adafruit_DHT as ada
import pandas as pd
import csv
import sys
import argparse
from statistics import fmean
from socket import socket, AF_INET, SOCK_DGRAM
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('average', type=int, default=6)
parser.add_argument('logging', type=str, default='log.csv')
parser.add_argument('hum_min', type=float, default=40)
parser.add_argument('hum_max', type=float, default=50)
parser.add_argument('hum_dev', type=float, default=5)
parser.add_argument('temp_min', type=float, default=20.0)
parser.add_argument('temp_max', type=float, default=24.0)
parser.add_argument('temp_dev', type=float, default=1)
args = parser.parse_args()

DHT_SENSOR = ada.DHT11
INSIDE_DHT_PIN = 4
OUTSIDE_DHT_PIN = 24

SERVER_IP   = '192.168.0.17'
PORT_NUMBER = 5000
SIZE = 1024
mySocket = socket( AF_INET, SOCK_DGRAM )
# print ("Test client sending packets to IP {0}, via port {1}\n".format(SERVER_IP, PORT_NUMBER))

def write_csv(in_hum, in_temp, out_hum, out_temp):
    f = open(args.logging, 'a', newline='')
    writer = csv.writer(f)    
    writer.writerow([in_hum, in_temp, out_hum, out_temp, datetime.now()])  
    f.close()
    print("average values: ", in_hum, in_temp, out_hum, out_temp, datetime.now())
    #print(f.closed)

def open_message(in_hum, in_temp, out_hum, out_temp):
    messages = {
        "dry": "too dry, open window",
        "humid": "too humid, open window",
        "cold": "too cold, open window",
        "hot": "too hot, open window"
    }
    if in_hum < args.hum_min and out_hum >= (args.hum_min + args.hum_dev):
        return messages['dry']
    elif in_hum > args.hum_max and out_hum <= (args.hum_max - args.hum_dev):
        return messages['humid']
    elif in_temp < args.temp_min and out_temp >= (args.temp_min + args.temp_dev):
        return messages['cold']
    elif in_temp > args.temp_max and out_temp <= (args.temp_min - args.temp_dev):
        return messages['hot']
    else: 
        return None

def close_message(in_hum, in_temp, out_hum, out_temp):  
    messages = {
        "close": ""
    }
    print()
    
if __name__ == "__main__":
    while True:
        in_hum_lst = []
        in_temp_lst = []
        out_hum_lst = []
        out_temp_lst = []
        open_flag = False

        for i in range(args.average):
            # read the humidity and temperature from the sensor
            in_hum, in_temp = ada.read_retry(DHT_SENSOR, INSIDE_DHT_PIN)
            out_hum, out_temp = ada.read_retry(DHT_SENSOR, OUTSIDE_DHT_PIN)

            # optional discarding of unrealistic/inaccurate values
            in_hum_lst.append(in_hum)
            in_temp_lst.append(in_temp)
            out_hum_lst.append(out_hum)
            out_temp_lst.append(out_temp)
            # print(in_hum,in_temp,out_hum,out_temp)

        avg_in_hum = fmean(in_hum_lst)
        avg_in_temp = fmean(in_temp_lst)
        avg_out_hum = fmean(out_hum_lst)
        avg_out_temp = fmean(out_temp_lst)

        write_csv(in_hum, in_temp, out_hum, out_temp)

        if open_flag is True:
            # message = close_message(avg_in_hum, avg_in_temp, avg_out_hum, avg_out_temp)
            message = "close the window"
        else:
            message = open_message(avg_in_hum, avg_in_temp, avg_out_hum, avg_out_temp)

        if message is not None:
            open_flag = not open_flag
        else: 
            message = "current inside temp and humidity is good " + str(in_temp) + "*C " + str(in_hum) + "%"

        # send the message
        mySocket.sendto(message.encode('utf-8'),(SERVER_IP,PORT_NUMBER))
    

