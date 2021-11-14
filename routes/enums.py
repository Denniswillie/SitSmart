import enum


# Status codes for server side to return to client side
class StatusCode(enum.IntEnum):
    INTERNAL_ERR_CODE: int = 500
    OK_STATUS_CODE: int = 200
    SUCCESSFUL_CREATION_STATUS_CODE: int = 201
