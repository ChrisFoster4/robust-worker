import socket

# Port numbers are arbitary (outside of avoiding reserved ports) but must be the same for every node on the network

# Can't use proper socket.SO_BROADCAST port as this requires root
BROADCAST_OUT_PORT = 56433
# BROADCAST_IN_PORT = 56434

COLLEAGUE_LISTEN_PORT = 56435
COLLEAGUE_TALK_PORT = 56436

BROADCAST_ASK_FOR_COLLEAGUE = "COLL_REQ"

COLLEAGUE_ADVERT_RESPONSE = "AVALIABLE_TO_COLLEAGUE"
COLLEAGUE_ADVERT_CONFIRMATION = "COLL_ADVERT_CONFIRM_REQ"
COLLEAGUE_REQUEST_PROGRESS = "COLL_GIVE_PROG"

LOCALHOST_NAME = socket.gethostname()
