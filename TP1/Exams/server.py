# Two threads: 
# 1 - for receiving messages or ACKs from the other machine's server and writing them to the DB
# 2 - for listening to the worklist and sending messages with the Exams reports and/or its state update

import socket
import mysql.connector
from hl7apy.parser import parse_message, parse_field

def get_id_from_msg():
    return 0

def remove_from_wl(id):
    mycursor=mydb.cursor()
    sql="DELETE FROM Worklist WHERE idWorkList=%s"    
    mycursor.execute(sql,id)
    print("pedido "+ str(id) +" removido da worklist")

def update_db(id, status, report):
    print("updated")


# BEGIN SCRIPT
s = socket.socket()
host = socket.gethostname()
port = 9090
s.bind((host,port))

mydb = mysql.connector.connect(
  host="Hostname",
  user="Username",
  passwd="Password",
  database="DB_Name"
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
