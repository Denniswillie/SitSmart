import enum


# Status codes for server side to return to client side
class StatusCode(enum.Enum):
    INTERNAL_ERR_CODE = 500
    OK_STATUS_CODE = 200
    SUCCESSFUL_CREATION_STATUS_CODE = 201
