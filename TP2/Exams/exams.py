import socket
import mysql.connector
from hl7apy import core
from hl7apy.consts import VALIDATION_LEVEL
from hl7apy.parser import parse_message, parse_field


def init_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="exams"
    )
    return db


def insert_db(id, msg):
    db = init_db()
    cursor = db.cursor()

    sql = "INSERT IGNORE INTO MessageHL7 (idMessageHL7, Message) VALUES (%s, %s)"
    val = (id, msg)

    cursor.execute(sql, val)
    db.commit()


# BEGIN SCRIPT

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 9999))

# become a server socket

serversocket.listen(5)
print("Waiting for connections.")

try:
    while True:
        c, addr = serversocket.accept()
        print("New connection from", addr, "\n")
        while True:
            msgBytes = c.recv(1024)
            if not msgBytes:
                break
            else:
                message = msgBytes.decode('utf-8')
                messageParsed = parse_message(message)

                msg = messageParsed.value
                id = messageParsed.msh.msh_10.value

                # update database
                insert_db(id, msg)

                # send ack
                hl7 = core.Message(
                    "ACK", validation_level=VALIDATION_LEVEL.STRICT)
                hl7.msh.msh_3 = "Exams"
                hl7.msh.msh_4 = "Exams"
                hl7.msh.msh_5 = "Requests"
                hl7.msh.msh_6 = "Request"
                hl7.msh.msh_10 = str(id)
                hl7.msh.msh_9 = "ACK"
                hl7.msh.msh_11 = "P"
                hl7.msa.msa_2 = str(id)
                hl7.msa.msa_1 = "AA"

                c.send(hl7.value.encode('utf-8'))
        c.close()

except KeyboardInterrupt:
    serversocket.shutdown(socket.SHUT_RDWR)
    serversocket.close()
