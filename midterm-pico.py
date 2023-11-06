# midterm-pico.py
import mqtt
import time
import network, ubinascii
from secrets import Tufts_Wireless as wifi
import gamepad_test
import urequests
from machine import Pin, PWM, I2C, ADC
import math

fan_servo = PWM(Pin(15))
fan_servo.freq(50)
high_pin = Pin(26, Pin.OUT)
high_pin.on()
thermistor_pin = Pin(27, Pin.IN)
thermistor = ADC(thermistor_pin)
cel_pin = Pin(19, Pin.OUT)
far_pin = Pin(20, Pin.OUT)




def connect_wifi(wifi):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
    print("MAC " + mac)

    station.connect(wifi['ssid'], wifi['pass'])
    while not station.isconnected():
        time.sleep(1)
    print('Connection successful')
    print(station.ifconfig())


# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected")
#     else:
#         print("Failed to connect, return code %d\n", rc)

def num_to_range(num, inMin, inMax, outMin, outMax):
  return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax
                  - outMin))


def get_temp():
    resist = 1000
    c1 = 1.009249522e-03
    c2 = 2.378405444e-04
    c3 = 2.019202697e-07
    #thermistor_resist = 10000 #10k ohms
    
    val = thermistor.read_u16()
    val = resist * (65535.0/float(val) - 1.0)
    log_val = math.log(val)
    Tc = (1.0 / (c1 + c2*log_val + c3*log_val*log_val*log_val))
    Tc = Tc - 273.15
    adjustment = 70
    Tc = Tc - adjustment
    #print("         " + str(val))
    #val = num_to_range(val, 30000, 36000, 20, 60)
    #print(Tc)
    time.sleep(.1)
    return int(Tc)


def sControl(cent):
    return int((float(cent) / 100) * 1800 + 4800)


def toggle_leds(toggle):
    if toggle:
        cel_pin.on()
        far_pin.off()
    else:
        far_pin.on()
        cel_pin.off()

def update_display(val, is_celsius, fan_on):
    print(val)
    fan_speed = num_to_range(val, 20, 33, 0, -100)
    fan_servo.duty_u16(sControl(fan_speed if fan_on else 0))
    print(fan_speed)
    toggle_leds(is_celsius)


def set_up_mqtt():
    broker_address = "io.adafruit.com"
    username = "jesenator"
    password = ""
    client_name = "pico client"
    # client = mqtt.Client(client_name)
    # client.on_connect = on_connect
    # client.username_pw_set(username, password)
    # client.connect(broker_address, 1883)

    fred = mqtt.MQTTClient(client_name, broker_address, user=username, password=password, keepalive=1000)
    fred.connect()
    print("mqtt connected")

    return fred


def read_i2c_device(last_x, last_y, last_btn):
    x = 1023 - gamepad_test.read_joystick(14)
    y = 1023 - gamepad_test.read_joystick(15)
    buttons = [not gamepad_test.digital_read() & btn for btn in gamepad_test.BTN_CONST]
    new_joystick_val = (abs(x - last_x) > 2) or (abs(y - last_y) > 2)

    new_button_val = False
    for btn, last, name in zip(buttons, last_btn, gamepad_test.BTN_Value):
        if (btn != last):  # if it has changed
            print(name)
            new_button_val = True
    is_new = new_joystick_val or new_button_val
    return is_new, x, y, buttons


def read_airtable():
    api_key = ''
    base_id = 'appiqDH9yo5f9lCwC'
    table_name = 'tblzIa6NVYGyQBPdr'
    record_id = 'rec4JEibPBPPGQJI6'

    # Headers to authenticate
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    endpoint = f'https://api.airtable.com/v0/{base_id}/{table_name}'
    response = urequests.get(endpoint, headers=headers)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response as JSON
        records = response.json().get('records', [])
        for record in records:
            id = record['id']
            name_text = record['fields']['Name']
    else:
        print(f'Error: {response.status_code}')

    return name_text


connect_wifi(wifi)
client = set_up_mqtt()
mins_till_next_read = 1
next_read_time = time.ticks_ms() + mins_till_next_read * 60 * 1000
airtable_updated = False
new_val, old_val = "", ""
x, y, buttons = 0, 0, [False] * len(gamepad_test.BTN_CONST)
temp = 0
is_celsius = True
party_mode = False
fan_on = True
toggle = True

while True:
    (is_new, x, y, buttons) = read_i2c_device(x, y, buttons)
    if buttons[0] == 1: #up
        party_mode = True
    if buttons[3] == 1: #down
        party_mode = False
    if buttons[2] == 1: #right
        fan_on = True
    if buttons[1] == 1: #left
        fan_on = False


    new_val = read_airtable()
    airtable_updated = (new_val != old_val)
    old_val = new_val
    is_celsius = (new_val == "C")
    
    print("getting temp")
    Tc = get_temp()
    temp = Tc if is_celsius else int((Tc * 9.0) / 5.0 + 32.0)
    
    if party_mode:
        toggle_leds(toggle)
        toggle = not toggle
        fan_servo.duty_u16(sControl(-100 if toggle else 100))
    else:

        update_display(Tc, is_celsius, fan_on)
    
    if time.ticks_ms() > next_read_time or airtable_updated:
        print("publishing")
        temp = Tc if is_celsius else int((Tc * 9.0) / 5.0 + 32.0)
        client.publish("jesenator/feeds/temp", str(temp))

        next_read_time = time.ticks_ms() + mins_till_next_read * 60 * 1000

    
    debug = True
    if debug:
        print(f'fan          : {"on" if fan_on else "off"}')
        print(f'party mode   : {"on" if party_mode else "off"}')
        print('gamepad values: %d %d %d %d %d %d' % (x, y, buttons[0], buttons[1], buttons[2], buttons[3]))
        print(f'airtable val : {new_val}')
        print(f'temp val     : {temp}')
        print("========================")
    time.sleep(.2)

client.disconnect()

