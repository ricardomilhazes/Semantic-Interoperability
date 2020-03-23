import mysql.connector
import socket
import threading
from hl7apy import core
from hl7apy.consts import VALIDATION_LEVEL
from hl7apy.parser import parse_message, parse_field
from dateutil.parser import parse
import time
import random
import string

global acks_gotten
acks_gotten = 0


def init_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="requests"
    )
    return db


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def create_HL7_msg(id):

    # Create Message
    hl7 = core.Message("ORM_O01", validation_level=VALIDATION_LEVEL.STRICT)

    # Message Header
    hl7.msh.msh_3 = "Requests"
    hl7.msh.msh_4 = "Requests"
    hl7.msh.msh_5 = "Exams"
    hl7.msh.msh_6 = "Exams"
    hl7.msh.msh_9 = "ORM^O01^ORM_O01"
    hl7.msh.msh_10 = str(id)
    hl7.msh.msh_11 = "P"

    # PID
    hl7.add_group("ORM_O01_PATIENT")
    hl7.ORM_O01_PATIENT.pid.pid_3 = randomString()
    hl7.ORM_O01_PATIENT.pid.pid_5 = randomString()
    hl7.ORM_O01_PATIENT.pid.pid_18 = randomString()
    hl7.ORM_O01_PATIENT.pid.pid_11 = randomString()
    hl7.ORM_O01_PATIENT.pid.pid_13 = randomString()
    # ORC
    hl7.ORM_O01_ORDER.orc.orc_1 = randomString()
    hl7.ORM_O01_ORDER.ORC.orc_10 = randomString()
    hl7.ORM_O01_ORDER.ORC.orc_2 = randomString()

    # OBX AND NTE
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.add_group("ORM_O01_OBSERVATION")
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_OBSERVATION.obx.obx_5 = randomString()
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_OBSERVATION.obx.obx_17 = randomString()
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_OBSERVATION.nte.nte_3 = randomString()

    assert hl7.validate() is True

    return hl7.value


def insert_db(id, msg, creation_time, sent_date):
    db = init_db()
    cursor = db.cursor()

    sql = "INSERT INTO MessageHL7 (idMessageHL7, Message, CreationTime, Sent, ReceivedAck) VALUES (%s, %s, %s, %s, NULL)"
    val = (id, msg, creation_time, sent_date)
    cursor.execute(sql, val)

    db.commit()


def update_db(id, received):
    db = init_db()
    cursor = db.cursor()

    print("RECEIVED:", received)

    sql = "UPDATE MessageHL7 SET ReceivedAck = %s WHERE idMessageHL7 = %s"
    val = (received, id)
    cursor.execute(sql, val)

    db.commit()


def ack_listener():
    global num
    global acks_gotten

    while acks_gotten < num:
        msgBytes = s.recv(1024)
        message = msgBytes.decode('utf-8')
        messageParsed = parse_message(message)
        if messageParsed.msh.msh_9.value == "ACK":
            id = messageParsed.msh.msh_10.value
            print(id, "- Received ACK")
            received = time.time()
            update_db(id, received)

            acks_gotten += 1


# BEGIN SCRIPT

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# exams server host and port:
host = 'localhost'
port = 9999
s.connect((host, port))

global num
num = int(input("How many HL7 messages you want to send?\n"))

ackThread = threading.Thread(target=ack_listener)
ackThread.start()


for i in range(0, num):
    creation_start = time.time()
    msg = create_HL7_msg(i)
    creation_time = time.time() - creation_start
    print(i, "- Creation time:", creation_time)

    print(msg)

    s.send(msg.encode('utf-8'))
    sent = time.time()
    print("SENT:", sent)

    insert_db(i, msg, creation_time, sent)

while acks_gotten < num:
    pass

print("Finished successfully.")
s.close()
