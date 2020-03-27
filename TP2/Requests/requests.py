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
import numpy as np
import os

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


def insert_db(id, msg, creation_time):
    db = init_db()
    cursor = db.cursor()

    sql = "INSERT INTO MessageHL7 (idMessageHL7, Message, CreationTime, Sent, ReceivedAck) VALUES (%s, %s, %s, NULL, NULL)"
    val = (id, msg, creation_time)
    cursor.execute(sql, val)

    db.commit()

    cursor.close()
    db.close()


def update_db_received(id, received):
    db = init_db()
    cursor = db.cursor()

    sql = "UPDATE MessageHL7 SET ReceivedAck = %s WHERE idMessageHL7 = %s"
    val = (received, id)
    cursor.execute(sql, val)

    db.commit()

    cursor.close()
    db.close()


def update_db_sent(id, sent):
    db = init_db()
    cursor = db.cursor()

    sql = "UPDATE MessageHL7 SET Sent = %s WHERE idMessageHL7 = %s"
    val = (sent, id)
    cursor.execute(sql, val)

    db.commit()

    cursor.close()
    db.close()


def worklist_listener():
    global num
    global acks_gotten
    global sec
    global queue_sizes

    while acks_gotten < num:
        # read rows from worklist every 5secs
        time.sleep(sec)
        db = init_db()
        cursor = db.cursor()

        getNewRows = "SELECT * FROM Worklist"
        cursor.execute(getNewRows)

        res = cursor.fetchall()

        size = cursor.rowcount

        if size > -1:
            queue_sizes.append(size)

        for request in res:
            s.send(request[1].encode('utf-8'))
            sent = time.time()
            print(request[0], "- SENT")
            update_db_sent(request[0], sent)

        cursor.close()
        db.close()


def remove_from_wl(id):
    db = init_db()
    cursor = db.cursor()
    sql = "DELETE FROM Worklist WHERE idWorklist=%s"
    cursor.execute(sql, (id,))
    print(id, "- REMOVED FROM WL")
    db.commit()
    cursor.close()
    db.close()


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
            update_db_received(id, received)
            remove_from_wl(id)

            acks_gotten += 1


def get_queue_stats(queue_sizes):
    print("\n\nWaiting Queue (every", sec, "seconds):")
    mu = np.mean(queue_sizes)
    median = np.median(queue_sizes)
    sigma = np.std(queue_sizes)
    max_val = np.amax(queue_sizes)
    min_val = np.amin(queue_sizes)
    print("MEAN:", mu)
    print("MEDIAN:", median)
    print("STD DEV:", sigma)
    print("MAX:", max_val)
    print("MIN:", min_val)


# BEGIN SCRIPT


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# exams server host and port:
host = 'localhost'
port = 9999
s.connect((host, port))

global num
num = int(input("How many HL7 messages you want to send?\n"))
# num = 100
global sec
sec = int(input("Worklist reading interval (in seconds)?\n"))
# sec = 3

global queue_sizes
queue_sizes = []

wlThread = threading.Thread(target=worklist_listener)
wlThread.start()
ackThread = threading.Thread(target=ack_listener)
ackThread.start()


for i in range(0, num):
    creation_start = time.time()
    msg = create_HL7_msg(i)
    creation_time = time.time() - creation_start
    # print(i, "- Creation time:", creation_time)

    # print(msg)

    insert_db(i, msg, creation_time)
    print(i, "- CREATED")


while acks_gotten < num:
    pass

print("Finished successfully.")

# Get queue size stats
get_queue_stats(queue_sizes)

s.close()
