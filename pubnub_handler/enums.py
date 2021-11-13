import enum


# Pubnub message types that will be handled when received by the subscriber
class MessageType(enum.Enum):
    CREATE_LOCATION = "CREATE_LOCATION"
    VERIFY_LOCATION_ID = "VERIFY_LOCATION_ID"
    GET_TABLE_INFO = "GET_TABLE_INFO"
    CREATE_TABLE = "CREATE_TABLE"
    REMOVE_TABLE = "REMOVE_TABLE"
    SAVE_TABLE_STATS = "SAVE_TABLE_STATS"
