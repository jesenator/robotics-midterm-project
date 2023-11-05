# midterm-computer-server.py
import requests
import paho.mqtt.client as mqtt
import time
import json
name_text = ""

base_id = 'appiqDH9yo5f9lCwC'
table_name = 'tblzIa6NVYGyQBPdr'
record_id = 'rec4JEibPBPPGQJI6'

# Headers to authenticate
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

endpoint = f'https://api.airtable.com/v0/{base_id}/{table_name}'


def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("Connected")
    else:
        print("Failed to connect, return code %d\n", rc)

broker_address = "io.adafruit.com"
client = mqtt.Client("pycharm server")
client.on_connect = on_connect

client.username_pw_set("jesenator", "aio_XvMJ50ILhQ9hsmgyD53CP598XWjc")
client.connect(broker_address, 1883)

client.loop_start()

while True:
    response = requests.get(endpoint, headers=headers)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response as JSON
        records = response.json().get('records', [])
        for record in records:
            print(record)
            id = record['id']
            print(id)
            name_text = record['fields']['Name']
            print(name_text)
    else:
        print(f'Error: {response.status_code}')

    client.publish("jesenator/feeds/temp_unit", "Fahrenheit" if name_text == "F" else "Celsius")
    time.sleep(5)

client.loop_stop()
client.disconnect()



# #################### updating record name
# endpoint = f'https://api.airtable.com/v0/{base_id}/{table_name}/{record_id}'
#
# data = {
#     "fields": {
#         "Name": "Ferry Building",
#     },
# }
# response = requests.patch(endpoint, headers=headers, data=json.dumps(data))
# if response.status_code == 200:
#     print('Successfully updated the record.')
#     updated_record = response.json()
#     print(json.dumps(updated_record, indent=4))
# else:
#     print(f'Failed to update the record: {response.status_code}')
#     print(response.json())
