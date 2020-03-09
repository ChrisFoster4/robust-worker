from worker import Worker
from netutils import is_alive, send_broadcast, send_message_to_colleague
from tests import tests
from globals import *
from master import Master

import socket
import threading
import time

unprocessed_broadcasts = []
messages_from_colleague = []
messages_from_master = []
current_colleague_progress = []


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


def master_listener():
    print("Listening for chatter from master on port:", FROM_MASTER_PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(('', FROM_MASTER_PORT))
    while True:
        message, address = s.recvfrom(FROM_MASTER_PORT)
        print("Received message from master", message.decode())
        messages_from_master.append((message.decode(), address))

def colleague_listener():
    print("Listening for chatter from colleague on port:", COLLEAGUE_LISTEN_PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(('', COLLEAGUE_LISTEN_PORT))
    while True:
        message, address = s.recvfrom(COLLEAGUE_LISTEN_PORT)
        # print("Received message from colleague", message.decode())
        messages_from_colleague.append((message.decode(), address))


def send_message_to_master(message):
    dest = (MASTER_ADDR, MASTER_DIRECT_PORT)

    print("Sending message to master:", message)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(message.encode(), dest)


def confirm_colleage(colleague_addr):
    send_message_to_colleague(colleague_addr, COLLEAGUE_ADVERT_CONFIRMATION)


def process_colleague_messages():
    if not messages_from_colleague:
        return

    while len(messages_from_colleague) != 0:

        message, from_addr = messages_from_colleague.pop()

        if message == COLLEAGUE_ADVERT_RESPONSE:
            print("Found avaliable colleague. Confirming with them now.")
            confirm_colleage(from_addr)
        elif message == COLLEAGUE_REQUEST_PROGRESS:
            send_message_to_colleague(COLLEAGUE, COLLEAGUE_PROGRESS_PREFIX + str(w.get_progress()))
        elif message.startswith(COLLEAGUE_PROGRESS_PREFIX):
            progress = message[:-len(COLLEAGUE_PROGRESS_PREFIX)]
            print("Colleague sent their progress:", progress)
            global current_colleague_progress
            current_colleague_progress = progress
            assert(len(current_colleague_progress) != 0)
        else:
            print("Unhandeled message from colleague:", message, " exiting now...")
            exit(1)


def process_broadcast():
    for (message, sender) in unprocessed_broadcasts:
        if message == BROADCAST_ASK_FOR_COLLEAGUE:
            print("Broadcast advert for colleague")
            if COLLEAGUE is None:
                respond_to_advert(sender)


def send_progress(worker):
    progress = worker.get_progress()
    send_message_to_colleague(COLLEAGUE, ''.join(progress))

def request_progress():
    if COLLEAGUE is None:
        pass
    send_message_to_colleague(COLLEAGUE, COLLEAGUE_REQUEST_PROGRESS)


def respond_to_advert(advertiser_address):
    send_message_to_colleague(advertiser_address, COLLEAGUE_ADVERT_RESPONSE)

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


def start_broad_listen():
    thread_exit = threading.Thread(target=broadcast_listener).start()
    if thread_exit is not None:
        print("Failed to spawn thread to listen for broadcasts with error string: ", thread_exit)
        exit(1)
    else:
        print("Broadcast listener running")

def start_colleage_and_master_listener():
    thread_exit = threading.Thread(target=master_listener).start()
    if thread_exit is not None:
        print("Failed to spawn thread to listen to master with error string: ", thread_exit)
        exit(1)
    else:
        print("Master listener running")

    thread_exit = threading.Thread(target=colleague_listener).start()
    if thread_exit is not None:
        print("Failed to spawn thread to listen to colleague with error string: ", thread_exit)
        exit(1)
    else:
        print("Colleague listener running")

def master_main():
    start_broad_listen()
    print("Master is running...")
    m = Master()
    m.listen()


def slave_main():
    assert (is_alive(MASTER_ADDR))
    start_broad_listen()
    start_colleage_and_master_listener()
    print("Listener threads all spawned successfully")

    global COLLEAGUE
    if LOCALHOST_NAME == "robust_1":
        COLLEAGUE = "robust_2"
    elif LOCALHOST_NAME == "robust_2":
        COLLEAGUE = "robust_1"

    global w
    w = Worker()
    since_sync = 0
    while True:
        if len(messages_from_master) == 0:
            send_message_to_master(SLAVE_REQ_WORK)
            time.sleep(1)
        else:
            if since_sync > SYNC_THRESHOLD:

                global current_colleague_progress
                foobar = current_colleague_progress
                current_colleague_progress = []
                send_message_to_colleague(COLLEAGUE, COLLEAGUE_REQUEST_PROGRESS)
                recieved = False
                for x in range(0,5):
                    process_colleague_messages()
                    time.sleep(1)
                    if len(current_colleague_progress) != 0:
                        recieved=True
                        break
                if not recieved:
                    print("Didn't recieve colleague progress as expected!")
                    print("Checking if they are alive!")
                    if not is_alive(COLLEAGUE):
                        print("Colleague:", COLLEAGUE, " appears to have died!!")
                        print("Progress was : ", foobar)
                    exit(1)


            since_sync = since_sync + 1
            block_start = messages_from_master.pop(0)[0]
            w.work(block_start)



def main():
    print("Robust worker running")

    if LOCALHOST_NAME == "master":
        master_main()
    else:
        slave_main()


# tests()
main()
