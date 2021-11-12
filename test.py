import os
from getmac import get_mac_address as gma
import uuid

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

CHANNEL = "sitsmart_sensors_data_channel"

pubnub_config = PNConfiguration()
pubnub_config.publish_key = "pub-c-94051755-9540-4114-bbc2-58edb0260e91"
pubnub_config.subscribe_key = "sub-c-fe5caef8-3a61-11ec-b2c1-a25c7fcd9558"
pubnub_config.uuid = str(uuid.uuid4())

pubnub = PubNub(pubnub_config)

action_types = ["GET_TABLE_INFO", "CREATE_TABLE"]

def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass
class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, event):
        pass
    def status(self, pubnub, event):
        pass

    def message(self, pubnub, event):
        # Handle new message stored in message.message
        try:
            msg = event.message
            if "type" in msg:
                self.handle_event(msg)
            else:
                raise Exception("Type attribute does not exist in response")
        except Exception as e:
            print(e)
            pass

    def handle_event(self, msg):
        if msg["type"] in action_types:
            if msg["type"] == "GET_TABLE_INFO":
                study_table_info = msg["study_table_info"]
                study_table_name = study_table_info["study_table_name"]
            elif msg["type"] == "CREATE_TABLE":
                study_table_id = msg["study_table_id"]
                print("The study table id is: ", study_table_id)
        else:
            print("Server responded with an action type that is not recognised")

pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels(CHANNEL).execute()
mac_address = gma()
pubnub.publish().channel(CHANNEL).message({"type": "GET_TABLE_INFO","pi_mac_address": mac_address, "sender": pubnub.uuid}).sync()