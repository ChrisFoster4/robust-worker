from worker import Worker
from netutils import is_alive, send_broadcast
from tests import tests
from globals import *

import socket
import threading
import time

unprocessed_broadcasts = []
messages_from_colleague = []


def broadcast_listener():
    print("Listening for broadcasts on port:", BROADCAST_OUT_PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(('', BROADCAST_OUT_PORT))
    while True:
        message, address = s.recvfrom(BROADCAST_OUT_PORT)
        print("Received broadcast:", message.decode())
        unprocessed_broadcasts.append((message.decode(), address))
        # Can't do any work here. We MUST get straight back to listening so we don't miss anything


def colleague_listener():
    print("Listening for chatter from colleague on port:", COLLEAGUE_LISTEN_PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(('', COLLEAGUE_LISTEN_PORT))
    while True:
        message, address = s.recvfrom(COLLEAGUE_LISTEN_PORT)
        print("Received message from colleague", message.decode())
        messages_from_colleague.append((message.decode(), address))


def send_message_to_colleague(message):
    dest = (COLLEAGUE, COLLEAGUE_LISTEN_PORT)
    if COLLEAGUE is None:
        print("Can't send message to colleague as they are None")
        return

    print("Sending message to colleague:", COLLEAGUE)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(message.encode(), dest)


def confirm_colleage(colleague_addr):
    COLLEAGUE = colleague_addr
    send_message_to_colleague(COLLEAGUE_ADVERT_CONFIRMATION)


def process_colleague_messages():
    if not messages_from_colleague:
        return

    for message, from_addr in messages_from_colleague:
        if message == COLLEAGUE_ADVERT_RESPONSE:
            print("Found avaliable colleague. Confirming with them now.")
            confirm_colleage(from_addr)


def process_broadcast():
    for (message, sender) in unprocessed_broadcasts:
        if message == BROADCAST_ASK_FOR_COLLEAGUE:
            print("Broadcast advert for colleague")
            if COLLEAGUE is None:
                respond_to_advert(sender)


def send_progress(worker):
    progress = worker.get_progress()
    send_message_to_colleague(''.join(progress))


def request_progress():
    if COLLEAGUE is None:
        pass
    send_message_to_colleague(COLLEAGUE_REQUEST_PROGRESS)
    pass


def respond_to_advert(advertiser_address):
    global COLLEAGUE
    COLLEAGUE = advertiser_address
    send_message_to_colleague(COLLEAGUE_ADVERT_RESPONSE)


def pick_colleague():
    pass


def ask_for_colleague():
    send_broadcast(BROADCAST_ASK_FOR_COLLEAGUE)
    while COLLEAGUE is None:
        process_broadcast()
        time.sleep(1)

        # Failed to get a colleague. Lets try again.
        send_broadcast(BROADCAST_ASK_FOR_COLLEAGUE)

    # TODO process colleague(s)


def main():
    print("Robust worker running")
    thread_exit = threading.Thread(target=broadcast_listener).start()
    if thread_exit is not None:
        print("Failed to spawn thread to listen for broadcasts with error string: ", thread_exit)
        exit(1)
    else:
        print("Broadcast listener running")

    thread_exit = threading.Thread(target=colleague_listener).start()
    if thread_exit is not None:
        print("Failed to spawn thread to listen to colleague with error string: ", thread_exit)
        exit(1)
    else:
        print("Colleague listener running")

    # thread_exit = threading.Thread(target=)
    # if thread_exit is not None:
    #     print("Failed to create broadcast handeler thread with error string", thread_exit)
    #     exit(1)
    # else:
    #     print("Broadcast handeler thread spawned")
    #
    global COLLEAGUE
    if LOCALHOST_NAME == "holt":
        COLLEAGUE = "192.168.0.29"
        assert (is_alive(COLLEAGUE))
        # time.sleep(1)
        send_broadcast("hello world")
        send_broadcast(BROADCAST_ASK_FOR_COLLEAGUE)
        send_message_to_colleague("hello there")
        # ask_for_colleague()
    else:
        COLLEAGUE = "192.168.0.25"
        assert (is_alive(COLLEAGUE))
        # time.sleep(1)
        send_broadcast("hello hell")
        send_message_to_colleague("General Kenobi")

    # w = Worker.work()


tests()

main()

