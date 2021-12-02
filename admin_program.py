from dotenv import load_dotenv
import os
from getmac import get_mac_address as gma
import uuid
import requests
import json

from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

load_dotenv()

CHANNEL = "sitsmart_sensors_data_channel"

pubnub_config = PNConfiguration()
pubnub_config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
pubnub_config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
pubnub_config.uuid = str(uuid.uuid4())

pubnub = PubNub(pubnub_config)
location_id = None
study_table_id = None

res = requests.post("https://sitsmart.tk/pubnub_token", data={"client_uuid": pubnub.uuid})
token = json.loads(res.text)["token"]
pubnub.set_token(token)


try:
    def handle_event(msg):
        global location_id, study_table_id
        if msg["type"] == "VERIFY_LOCATION_ID":
            if msg["verified"]:
                location_id = msg["location_id"]
                get_table_info()
            else:
                print("Entered location_id is not verified.")
                location_screen()
        elif msg["type"] == "CREATE_LOCATION":
            location_id = msg["location_id"]
            get_table_info()
        elif msg["type"] == "GET_TABLE_INFO":
            # study table is not registered
            study_table_id = msg["study_table_info"]["study_table_id"]
            if not study_table_id:
                create_study_table_screen()
            else:
                # Continue to remove table screen
                study_table_operation_screen()

        elif msg["type"] == "CREATE_TABLE":
            # table name has already existed in the same location
            if msg["study_table_id"] == -1:
                print(
                    "Table with the same name has already been registered in the same location, please enter a different table name")
                print("#############################################################################################")
                create_study_table_screen()
            else:
                study_table_id = msg["study_table_id"]
                study_table_operation_screen()
        elif msg["type"] == "REMOVE_TABLE":
            if msg["removed"]:
                print("Successfully removed table.")
                get_table_info()
                study_table_id = None
            else:
                print("Failed to remove the study table. Please try again.")
                study_table_operation_screen()
        else:
            print("Server responded with an action type that is not recognised")


    class MySubscribeCallback(SubscribeCallback):
        def presence(self, pubnub, event):
            pass

        def status(self, pubnub, event):
            pass

        def message(self, pubnub, event):
            # Handle new message stored in message.message
            if "receiver" in event.message and pubnub.uuid == event.message["receiver"]:
                msg = event.message
                if "type" in msg:
                    handle_event(msg)
                else:
                    raise Exception("Type attribute does not exist in response")


    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels(CHANNEL).execute()

    pi_mac_address = gma()


    def location_screen():
        while True:
            print("Welcome to the SitSmart admin dashboard!")
            print("Please choose one of the options:")
            print("1. I have a location id")
            print("2. I don't have a location id, will need to create a location")
            input_num = int(input("Please enter number here: "))
            if input_num == 1:
                # Not save it as the location_id since it still needs to be verified
                temp_location_id = int(input("Please enter the location id: "))
                pubnub.publish().channel(CHANNEL).message({
                    "type": "VERIFY_LOCATION_ID",
                    "location_id": temp_location_id,
                    "sender": pubnub.uuid
                }).sync()
                break
            elif input_num == 2:
                location_name = input("Please enter the location name: ")
                pubnub.publish().channel(CHANNEL).message({
                    "type": "CREATE_LOCATION",
                    "location_name": location_name,
                    "sender": pubnub.uuid
                }).sync()
                break
            else:
                print("Option does not exist, are you blind?")


    def get_table_info():
        pubnub.publish().channel(CHANNEL).message({
            "sender": pubnub.uuid,
            "type": "GET_TABLE_INFO",
            "pi_mac_address": pi_mac_address,
        }).sync()


    def create_study_table_screen():
        print("It seems that your table is not registered yet.")
        print("Here are the following options:")
        print("1. Create study table entry (You need to enter the name)")
        print("2. Quit program")
        input_num1 = input("Please enter number here: ")
        input_num = int(input_num1)
        if input_num == 1:
            study_table_name = input("Enter study table name: ")
            print("Creating study table...")
            pubnub.publish().channel(CHANNEL).message({
                "sender": pubnub.uuid,
                "type": "CREATE_TABLE",
                "study_table_name": study_table_name,
                "pi_mac_address": pi_mac_address,
                "location_id": location_id
            }).sync()
        else:
            pubnub.stop()
            os._exit(0)


    def study_table_operation_screen():
        global study_table_id
        print("Welcome to your study table dashboard.")
        print("Choose the operation you wish to do with your table:")
        print("1. Remove study table")
        print("2. Quit program")
        input_num = int(input("Please enter number here: "))
        if input_num == 1:
            pubnub.publish().channel(CHANNEL).message({
                "sender": pubnub.uuid,
                "type": "REMOVE_TABLE",
                "pi_mac_address": pi_mac_address,
                "study_table_id": study_table_id
            }).sync()
        elif input_num == 2:
            pubnub.stop()
            os._exit(0)
        else:
            print("Chosen number does not exist, please enter a valid number!")


    location_screen()

    # Ask the location id from the user. If the user doesn't have a location id, the user can create a location
    # by entering the location name. This location name will then be sent to the server through pubnub. The server
    # creates a new location and a new id for it. The new location id is sent back to the admin. If the admin already
    # has a location id, the admin needs to send the location id (to verify if such location id exists). The server
    # will send back a response if that location id exists or not. If not, then, repeat this paragraph.

    # At this point, a location id is already saved in a variable in memory. Right when the location id is saved to
    # the variable, the raspberry pi will try to get the table info, just to see if the table has been registered. 2
    # cases here, the first one is if the table id has not been registered. In this case, the admin will need to
    # enter a study table name in order to create a table. The admin will then send the study table name,
    # the location id, and the mac address of the raspberry pi to the server to create the table. If there's already
    # an existing table name, the server will send None as the study table id. If successful, the server will send
    # the newly created study table id.

    # At this point, the admin already has a study table id. The admin will need to be given the ability to remove
    # the table. If the admin wants to remove the table, the admin will need to input study table id and also the mac
    # address. The mac address is needed to verify that the remover is the appropriate table admin.
except:
    os._exit(0)
