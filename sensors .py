import time
import board
import busio
import adafruit_sgp30
import adafruit_dht
import psutil
import time
from getmac import get_mac_address as gma
# !/usr/bin/python
import RPi.GPIO as GPIO
import requests
import json
import os
from dotenv import load_dotenv

from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
load_dotenv()
pubnub_channel = "sitsmart_sensors_data_channel"

pubnub_config = PNConfiguration()
pubnub_config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
pubnub_config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
pubnub_config.uuid = str(uuid.uuid4())

pubnub = PubNub(pubnub_config)

channel = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
milis_last = None
counter = 0

# We first check if a libgpiod process is running. If yes, we kill it!
for proc in psutil.process_iter():
    if proc.name() == 'libgpiod_pulsein' or proc.name() == 'libgpiod_pulsei':
        proc.kill()

sensor = adafruit_dht.DHT11(board.D23)

i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

sgp30.iaq_init()
sgp30.set_iaq_baseline(0x8973, 0x8AAE)

elapsed_sec = 0

averageSound = 0
totalSoundSample = 0

response = requests.post("https://sitsmart.tk/studyTable/getInfo", data={
	"mac_address": gma()
})
response_dict = json.loads(response)
study_table_id = None
if response_dict["statusCode"] == 400:
	raise Exception("Caused by internal server error.")
elif response_dict["result"]["study_table_id"] == None:
	raise Exception("The study table has not been registered yet.")

def publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


lastTime = time.time()
while True:
    currTime = time.time()
    if currTime - lastTime > 3600:
        while True:
            published = False
            try:
                pubnub.publish().channel(pubnub_channel).message({
                	"study_table_id": study_table_id,
                	"recorded_time": recorded_time,
                	"temperature_level": sensor.temperature,
                	"co2_level": sgp30.eCO2,
                	"sound_level": averageSound
                }).sync()
                published = True
            except Exception as e:
                if int(e._status_code) == 403:
                    # token is either expired or has not set a token
                    res = requests.post("https://sitsmart.tk/pubnub_token", data={"client_uuid": pubnub.uuid})
                    token = json.loads(res.text)["token"]
                    pubnub.set_token(token)
                else:
                    raise Exception(e)
            if published:
                break

        averageSound = totalSoundSample = 0
        lastTime = currTime

    milis_current = time.time() * 1000
    milis_elapsed = milis_current - milis_last if milis_last is not None else 0
    if milis_last is None:
        milis_last = milis_current
    if not GPIO.input(channel):
        counter += 1
    if milis_elapsed > 10:
        print(counter)
        averageSound = ((averageSound * totalSoundSample) + counter) / (totalSoundSample + 1)
        totalSoundSample += 1
        print(averageSound)
        counter = 0
        milis_last = milis_current
