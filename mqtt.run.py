#!/usr/bin/python3
import sys, time, os, threading, shutil, datetime, math
import numpy as np
import src.mqtt_lib as mqtt_lib



if __name__ == '__main__':
    test_str="{'applicationID': '3', 'applicationName': 'C2127A8480B1FF04', 'devEUI': '5678567856785678', 'deviceName': 'Temp-1', 'timestamp': 1638047728, 'fCnt': 1, 'fPort': 2, 'data': '22', 'data_encode': 'hexstring', 'adr': False, 'rxInfo': [{'gatewayID': 'ac1f09fffe060aa4', 'loRaSNR': 8.8, 'rssi': -22, 'location': {'latitude': 0.0, 'longitude': 0.0, 'altitude': 0}}], 'txInfo': {'frequency': 867300000, 'dr': 0}}"
    host_ip = '192.168.230.1'
    mqtt = mqtt_lib.MQTT_Module(host_ip)
    mqtt.subscribe(1,0)

### Ex. python3 mqtt.run.py 
