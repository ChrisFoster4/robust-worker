import subprocess
import socket

BROADCAST_OUT_PORT = 56433


def is_alive(address):
    # GNU Coreutils specific ping arguments
    process = subprocess.Popen('ping -c 1 -w 1 %s' % address, stdout=subprocess.PIPE, shell=True)

    # Block until done
    process.communicate()[0]
    rc = process.returncode
    return rc == 0


def send_broadcast(message):
    dest = ('<broadcast>', BROADCAST_OUT_PORT)
    print("Sending on port", BROADCAST_OUT_PORT)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(message.encode(), dest)
