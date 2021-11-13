from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub
from pubnub_handler.enums import MessageType
from pubnub_handler.utils import get_table_info, create_table, remove_table, save_table_stats, create_location, verify_location_id
from flask import Flask
from entities import StudyTableInfo


# pubnub client wrapper
class PubnubHandler:
    def __init__(self, mysql, config, app):
        self._mysql = mysql
        self._pubnub = PubNub(config)
        self._app = app

    # Subscribing the pubnub client to the channel.
    # This should be ran in a separate thread, otherwise it will block the main thread causing
    # other operations to be halted.
    def subscribe(self, channel):
        class PubnubHandlerSubscribeCallback(SubscribeCallback):
            def __init__(self, app: Flask, mysql):
                SubscribeCallback.__init__(self)
                self._app = app
                self._mysql = mysql

            def presence(self, pubnub, event):
                pass

            def status(self, pubnub, event):
                pass

            def message(self, pubnub, event):
                if event.message and type(event.message) == dict and "type" in event.message:
                    # Need to provide an app context in order to get the mysql connection cursor.
                    with self._app.app_context():
                        if "sender" in event.message and event.message["sender"] != pubnub.uuid:
                            if event.message["type"] == MessageType.CREATE_LOCATION.name:
                                pubnub.publish().channel(channel).message({
                                    "type": MessageType.CREATE_LOCATION.name,
                                    "sender": pubnub.uuid,
                                    "location_id": create_location(event.message, self._mysql)
                                })
                            elif event.message["type"] == MessageType.VERIFY_LOCATION_ID.name:
                                pubnub.publish().channel(channel).message({
                                    "type": MessageType.VERIFY_LOCATION_ID.name,
                                    "sender": pubnub.uuid,
                                    "verified": verify_location_id(event.message, self._mysql),
                                    "location_id": event.message["location_id"]
                                })
                            elif event.message["type"] == MessageType.GET_TABLE_INFO.name:
                                study_table_info = get_table_info(event.message, self._mysql)
                                pubnub.publish().channel(channel).message({
                                    "study_table_info": study_table_info.__dict__,
                                    "type": MessageType.GET_TABLE_INFO.name,
                                    "sender": pubnub.uuid
                                }).sync()
                            elif event.message["type"] == MessageType.CREATE_TABLE.name:
                                study_table_id = create_table(event.message, self._mysql)
                                pubnub.publish().channel(channel).message({
                                    "study_table_id": study_table_id,
                                    "type": MessageType.CREATE_TABLE.name,
                                    "sender": pubnub.uuid
                                }).sync()
                            elif event.message["type"] == MessageType.REMOVE_TABLE.name:
                                remove_table(event.message, self._mysql)
                            elif event.message["type"] == MessageType.SAVE_TABLE_STATS.name:
                                save_table_stats(event.message, self._mysql)

        self._pubnub.add_listener(PubnubHandlerSubscribeCallback(self._app, self._mysql))
        self._pubnub.subscribe().channels(channel).with_presence().execute()
