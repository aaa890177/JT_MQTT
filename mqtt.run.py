import src.mqtt_lib as mqtt_lib
import os
import time
import json


with open('config/config.json','r') as f:
    config_dict = json.load(f)

if __name__ == '__main__':
    time_mark =  time.strftime( "%Y.%m.%d_%X", time.localtime() ).replace(":", "")
    filename = '%s_mqttlog.txt'%time_mark
    logfile = os.path.join(os.getcwd(), 'mqttlog', filename)
    host_ip = config_dict['IP']
    mqtt = mqtt_lib.MQTT_Module(host_ip, logfile = logfile)
    mqtt.subscribe(1,0)
 
