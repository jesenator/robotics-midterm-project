# midterm-pico.py
import mqtt
import time
import network, ubinascii
from secrets import Tufts_Wireless as wifi
import gamepad_test


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


def get_temp():
    return 30


def update_display(val):
    pass


def set_up_mqtt():
    broker_address = "io.adafruit.com"
    username = "jesenator"
    password = "-------"
    client_name = "pico client"
    # client = mqtt.Client(client_name)
    # client.on_connect = on_connect
    # client.username_pw_set(username, password)
    # client.connect(broker_address, 1883)

    fred = mqtt.MQTTClient(client_name, broker_address, user=username, password=password, keepalive=1000)
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
    if new_joystick_val or new_button_val:
        msg = '%d %d %d %d %d %d' % (x, y, buttons[0], buttons[1], buttons[2], buttons[3])
        print(msg)
    return x, y, buttons


def read_airtable():
    val = ""
    return val


connect_wifi(wifi)
client = set_up_mqtt()
client.loop_start()
next_read_time = time.ticks_ms() + 5 * 60 * 1000
airtable_updated = False
new_val, old_val = "", ""
last_x, last_y, last_btn = 0, 0, [False] * len(gamepad_test.BTN_CONST)

while True:
    if time.ticks_ms > next_read_time or airtable_updated:
        temp = get_temp()
        print("publishing")
        client.publish("jesenator/feeds/temp", temp)
        update_display(temp)
        time.sleep(3)

    (last_x, last_y, last_btn) = read_i2c_device(last_x, last_y, last_btn)
    new_val = read_airtable()

    airtable_updated = (new_val != old_val)
    old_val = new_val

client.loop_stop()
client.disconnect()
