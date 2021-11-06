from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub_handler.enums import MessageType
from pubnub_handler.utils import get_table_info, create_table, remove_table, edit_table_info, save_table_stats


# pubnub client wrapper
class PubnubHandler:
    def __init__(self, mysql, config):
        self._mysql = mysql
        self._pubnub = PubNub(config)

    # Subscribing the pubnub client to the channel.
    # This should be ran in a separate thread, otherwise it will block the main thread causing
    # other operations to be halted.
    def subscribe(self, channel):
        mysql = self._mysql
        pubnub = self._pubnub

        class PubnubHandlerSubscribeCallback(SubscribeCallback):
            def presence(self, pubnub, event):
                pass

            def status(self, pubnub, event):
                pass

            def message(self, pubnub, event):
                if "message" in event and "type" in event.message:
                    if event.message["type"] == MessageType.GET_TABLE_INFO.name:
                        study_table_info = get_table_info(event.message, mysql)
                        pubnub.publish().channel(channel).message(study_table_info).sync()
                    elif event.message["type"] == MessageType.CREATE_TABLE.name:
                        study_table_id = create_table(event.message, mysql)
                        pubnub.publish().channel(channel).message(study_table_id).sync()
                    elif event.message["type"] == MessageType.REMOVE_TABLE.name:
                        remove_table(event.message, mysql)
                    elif event.message["type"] == MessageType.SAVE_TABLE_STATS.name:
                        save_table_stats(event.message, mysql)

        self._pubnub.add_listener(PubnubHandlerSubscribeCallback())
        self._pubnub.subscribe().channels(channel).with_presence().execute()
