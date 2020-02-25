# For receiving ACKs and request updates from the other machine's server and then clearing the worklist

import socket
import mysql.connector
from hl7apy.parser import parse_message, parse_field

def get_id_from_msg():
    return 0

def remove_from_wl(id):
    print("removed")

def update_db(id, status, report):
    print("updated")


# BEGIN SCRIPT
s = socket.socket()
host = socket.gethostname()
port = 9090
s.bind(host,port)

mydb = mysql.connector.connect(
  host="localhost",
  user="yourusername",
  passwd="yourpassword",
  database="NOME_DA_DB"
)

# wait for connections
s.listen()

while True:
    c, addr = s.accept()
    msgBytes = c.recv(1024)
    message = parse_message(msgBytes)
    if parse_field(msgBytes,"MSH_9").to_er7() == "ACK":
        id = get_id_from_msg()
        remove_from_wl(id)
    else:
        # id = message.id
        # status = message.status
        # report = message.report
        id = 0
        status = 1
        report = 'test'
        update_db(id, status, report)
