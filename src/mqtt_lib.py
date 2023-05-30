import paho.mqtt.client as mqtt
import json, base64, codecs
import time, datetime
import re, ast



with open('topo/snsr_type_def.json', 'r') as f:
    unit_dict = json.load(f)



class MQTT_Module:
    def __init__(self, hostIP, appID='', devEUI='', sub_topic='', pub_topic='', client_id='', client_pw='', port=1883):
        self.hostIP = hostIP
        if sub_topic == '':
            # self.sub_topic = "application/%s/device/%s/rx" % (str(appID), devEUI.lower())
            self.sub_topic = "#"
        else:
            self.sub_topic = sub_topic
        if pub_topic == '':
            # self.pub_topic = "application/%s/device/%s/tx" % (str(appID), devEUI.lower())
            self.pub_topic = "#"
        else:
            self.pub_topic = pub_topic
        self.client_id = client_id
        self.client_pw = client_pw
        self.grep_key = ["fPort", "data", "frequency", "dr"]
        self.port = port
    
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
            client.loop_forever()
        return self.recv_list
    
    def publish(self, data):
        b64 = codecs.encode(codecs.decode(data, 'hex'), 'base64').decode().rstrip('\n')
        send = json.dumps(data)

        client = mqtt.Client()
        for i in range(3):
            try:
                if self.client_id != '':
                    client.username_pw_set(self.client_id, self.client_pw)
                client.connect(self.hostIP, self.port)
            except Exception as e:
                time.sleep(1)
                if i ==2 :
                    print('%s, \nFailed to connect to MQTT Broker...' %str(e))
                    return False

        print("Publish to %s " %(self.hostIP,data))
        client.publish(self.pub_topic, send)
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
                print('split data then put in handle_data list\n%s'%(f'{handle_data}'))
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
                        value += '\t%s_%s: %s%s'   %(CH_id, sensor_name, dec_data, unit)
                        snsr_id_index += (1+inner_dict['length'])
                    snsr_id_index += 1
                print(deviceName)
                print('devid:%s%s\n'%(dev_id, value))
        except:
            data = msg.payload.decode('utf-8') 
            print(data)

        if self.loop_forever != 1:
            self.recv_list.append(data)         
        
    def dashboard_data(self):
        dashboard_dict = {}
        for board in unit_dict['dashboard']:
            dashboard_dict[unit_dict[board]['name']] = globals()['df_%s'%unit_dict[board]['name']]
        return dashboard_dict




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
