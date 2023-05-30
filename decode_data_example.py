import re, json










# decode_method
with open('topo/snsr_type_def.json', 'r') as f:
    unit_dict = json.load(f)

json_file_path= {
    'Temperature_json'    : 'example_str/Temperature.json',
    'PH_json'             : 'example_str/PH.json',
    'Conductivity_json'   : 'example_str/Conductivity.json'
}

def twosComplement_hex(hexval):
    bits = 16
    val = int(hexval, bits)
    if val & (1 << (bits-1)):
        val -= 1 << bits
    return val

def json_decode(json_file):
    # print('Json : ',json.dumps(data, sort_keys=True, indent=4, separators=(', ', ': ')),'\n') # Json 格式化
    deviceName = json_file['deviceName']# deviceName in here
    dev_id, value= decode(json_file['data'])
    print(deviceName)
    print('devid:%s%s\n'%(dev_id, value))
    print('-'*100)

def decode(data):
    value = ''
    pattern = re.compile('.{2}')
    handle_data = pattern.findall(data)
    # print('split data then put in handle_data list\n%s\n'%(f'{handle_data}'))
    dev_id = int(handle_data[0], 16) # device id in here
    snsr_id_index = 1
    while (snsr_id_index+1) < len(handle_data) and '\r' not in json_file:
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
    return dev_id, value

for i in json_file_path:
    print('now decode file = %s\n'%json_file_path[i])
    with open(json_file_path[i]) as f:
        json_file = json.load(f)
        json_decode(json_file)

while True:
    data = input('input data: ')
    try:
        dev_id, value= decode(data)
        print('devid:%s%s\n'%(dev_id, value))
        print('-'*100)
    except:
        print('invalid')



