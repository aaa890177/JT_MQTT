import src.mqtt_lib as mqtt_lib
import os
import time
import json
import paho.mqtt.client as mqtt
import threading



def pub_to_adawirless(data):
    ada_client = mqtt.Client()
    ada_client.connect('www.adawireless.com')
    ada_client.publish('jt_log',data)
    ada_client.disconnect()

with open('config/config.json','r') as f:
    config_dict = json.load(f)

if __name__ == '__main__':
    time_mark =  time.strftime( "%Y.%m.%d_%X", time.localtime() ).replace(":", "")
    filename = '%s_mqttlog.txt'%time_mark
    logfile = os.path.join(os.getcwd(), 'mqttlog', filename)
    host_ip = config_dict['IP']
    mqtt_class = mqtt_lib.MQTT_Module(host_ip, logfile = logfile)
    mqtt_class.subscribe(1,0)
    
    while True:
        if mqtt_class.recv_list != []:
            msg = mqtt_class.recv_list[0]
            mqtt_class.recv_list.clear()
            pub_task = threading.Thread(target=pub_to_adawirless, args=(msg,))
            pub_task.daemon =True
            pub_task.start()
        
 
