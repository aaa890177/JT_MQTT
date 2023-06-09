import paho.mqtt.client as mqtt
import json, base64, codecs
import time, datetime
import re, ast



with open('topo/snsr_type_def.json', 'r') as f:
    unit_dict = json.load(f)



class MQTT_Module:
    def __init__(self, hostIP, appID='', devEUI='', sub_topic='', client_id='', client_pw='', port=1883, logfile=''):
        self.hostIP = hostIP
        if sub_topic == '':
            # self.sub_topic = "application/%s/device/%s/rx" % (str(appID), devEUI.lower())
            self.sub_topic = "#"
        else:
            self.sub_topic = sub_topic
        self.logfile = logfile
        self.client_id = client_id
        self.client_pw = client_pw
        self.grep_key = ["fPort", "data", "frequency", "dr"]
        self.port = port
    
    # def get_recv():
        # if self.recv_list != []:
            # return_list = self.recv_list
            # self.recv_list.clear()
            # return return_list
    def subscribe(self, loop_forever=0, timeout=30):
        self.loop_forever = loop_forever
        if self.loop_forever==1:
            timeout= 'forever'
        print('Subscribe %s "%s" for %s sec' %(self.hostIP, self.sub_topic, timeout))
        self.recv_list = []
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        for i in range(3):
            try:
                if self.client_id != '':
                    client.username_pw_set(self.client_id, self.client_pw)
                client.connect(self.hostIP, self.port)
            except Exception as e:
                time.sleep(1)
                if i ==2 :
                    print(str(e))
                    print('Failed to connect to MQTT Broker...')
                    return False
        if self.loop_forever == 0:
            client.loop_start()
            #time_start = time.time()
            #while time.time() < (time_start + timeout):
            #    client.loop()
            time.sleep(timeout)
            client.loop_stop()
            client.disconnect()
            print('MQTT subscriber: End')
        else:
            # self.check_last_data()
            client.loop_start()
        return self.recv_list
   


    def publish(self, appID, devEUI, data):
        pub_topic = "application/%s/device/%s/tx" % (str(appID), devEUI.lower())
        send = json.dumps({"confirmed": False, "fPort": 10, "data": data})
        client = mqtt.Client()
        for i in range(3):
            try:
                if self.client_id != '':
                    client.username_pw_set(self.client_id, self.client_pw)
                client.connect('127.0.0.1', self.port)
            except Exception as e:
                time.sleep(1)
                if i ==2 :
                    print('%s, \nFailed to connect to MQTT Broker...' %str(e))
                    return False

        print("Publish to %s %s" %("127.0.0.1",data))
        client.publish(pub_topic, send)
        client.disconnect()



    def on_connect(self, client, userdata, flags, rc):
        #print("Connected with result code "+str(rc))
        client.subscribe(self.sub_topic)


    def on_message(self, client, userdata, msg):
        try :
            data = json.loads(msg.payload.decode("utf-8", 'ignore'))
            if 'data' in data:
                # print('Json : ',json.dumps(data, sort_keys=True, indent=4, separators=(', ', ': ')))
                deviceName = data['deviceName']  # deviceName in here

                data = data['data']
                value = ''
                pattern = re.compile('.{2}')
                handle_data = pattern.findall(data)
                # print('split data then put in handle_data list\n%s'%(f'{handle_data}'))
                dev_id = int(handle_data[0], 16) # device id in here
                snsr_id_index = 1
                while (snsr_id_index+1) < len(handle_data) and '\r' not in data:
                    ipso_index = snsr_id_index+1
                    if handle_data[ipso_index] not in unit_dict.keys():
                        pass
                    elif (len(handle_data[ipso_index-1:]) - (2+unit_dict[handle_data[ipso_index]]['length']) ) < 0:
                        pass
                    else:
                        CH_id = handle_data[ipso_index-1]# Channel id in here
                        inner_dict = unit_dict[handle_data[ipso_index]]
                        sensor_name = inner_dict['name']# sensor name in here
                        resolution = inner_dict['resolution']
                        unit = inner_dict['unit']
                        data_index = ipso_index+1
                        sensor_id_type = ''.join(i for i in handle_data[data_index-2: data_index])
                        hex_data = ''.join(i for i in handle_data[data_index: data_index+inner_dict['length']])
                        dec_data = round(twosComplement_hex(hex_data)*resolution,2) 
                        value += '\t%s_%s:%s%s'   %(CH_id, sensor_name, dec_data, unit)
                        snsr_id_index += (1+inner_dict['length'])
                    snsr_id_index += 1
                log_tmp = f'deviceName: {deviceName:15}devid:{dev_id}{value}'
                self.log(log_tmp, self.logfile)
        except:
            data = msg.payload.decode('utf-8') 
            self.log(data, self.logfile)      

        if self.loop_forever != 1:
            self.recv_list.append(log_tmp)         
        
    def dashboard_data(self):
        dashboard_dict = {}
        for board in unit_dict['dashboard']:
            dashboard_dict[unit_dict[board]['name']] = globals()['df_%s'%unit_dict[board]['name']]
        return dashboard_dict


    def log(self, log, path):
        
        time_mark =  time.strftime( "%Y.%m.%d_%X", time.localtime() )
        log = '[%s] %s'%(time_mark, log)
        f = open(path, 'a')
        print('\n%s'%log)
        print('\n%s'%log, file= f)
        self.recv_list.append(log)   
        f.close()

def twosComplement_hex(hexval):
    bits = 16
    val = int(hexval, bits)
    if val & (1 << (bits-1)):
        val -= 1 << bits
    return val







'''
import mqtt_lib as matt
matt = matt.MQTT_Module('169.254.26.109', '1', '0102030405066666')
result = matt.subscribe()
matt.publish('False', 1, '1abcddeadabcddead1')
'''
