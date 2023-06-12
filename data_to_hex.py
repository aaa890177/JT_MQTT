import re
import json
from paho.mqtt import client as mqtt
# aqua-2
# 180167017402A000FA03A100CA04A20085
# devid:24        01_T: 37.2      02_NACLO3: 25.0    03_HCL: 2.02    04_SG: 1.33
data = '{\"Timestamp\": \"2023/05/22 17:13:36\", \"S.G\": \"1.358\", \"HCL\": \"1.980\", \"NaClO3\": \"34.400\", \"Temperature\": \"35.200\"}'
# 0E 0167xxxx 02A0xxxx 03A1xxxx 04A2xxxx
# 01_T        = 01670160
# 02_NACLO3   = 02A00158
# 03_HCL      = 03A100C6
# 04_SG       = 04A20088
# 0E0167016002A0015803A100C604A20088
data ='2023/05/15 09:59:23      S.G = 1.348     HCl(M/L) = 1.970  NaClO3 = 38.000         TEMP(#) = 50.100'
def data_to_hex(data):
    pattern = r'\"(\d+\.\d+)\"'
    raw_list = re.findall(pattern, data)
    # print(*raw_list)
    value_list = []
    for val in raw_list:
        val =round(float(val),2)
        val = re.sub('\.','',str(val))
        hexadecimal_number = hex(int(val))[2:]
        formatted_values = str(hexadecimal_number).zfill(4)
        value_list.append(formatted_values.upper())
    value_={
        "01_T": value_list[3],
        "02_NACLO3": value_list[2],
        "03_HCL": value_list[1],
        "04_SG": value_list[0]
    }
    # for i in value_:print(value_[i])
    hex_str = f'0E0167{value_["01_T"]}02A0{value_["02_NACLO3"]}03A1{value_["03_HCL"]}04A2{value_["04_SG"]}'
    # print(hex_str)
    return hex_str


print(data_to_hex(data))
hex_data=data_to_hex(data)


send = json.dumps({"deviceName": "Aqua-2", "data": hex_data})
print(send)
pub_client = mqtt.Client()
pub_client.connect('127.0.0.1', 1883)
pub_client.publish('pub_topic', send)