import src.mqtt_lib as mqtt_lib
import os
import time
import json
import threading

time_mark =  time.strftime( "%Y.%m.%d_%X", time.localtime() ).replace(":", "")
filename = '%s_mqttlog.txt'%time_mark
logfile = os.path.join(os.getcwd(), 'mqttlog', filename)
host_ip = 'www.adawireless.com'
mqtt = mqtt_lib.MQTT_Module(host_ip, logfile= logfile)
mqtt.subscribe(1,0)

while True:
    if mqtt.recv_list != []:
        msg = mqtt.recv_list
        print(msg[0])
        mqtt.publish('123','123',msg[0])
        mqtt.recv_list.clear()
