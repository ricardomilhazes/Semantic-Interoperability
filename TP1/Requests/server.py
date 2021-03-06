# For receiving ACKs and request updates from the other machine's server and then clearing the worklist

import socket
import mysql.connector
from hl7apy import core
from hl7apy.consts import VALIDATION_LEVEL
from hl7apy.parser import parse_message, parse_field

def get_id_from_msg():
    return 0

def update_db(id, status, report):
    mycursor = mydb.cursor()
    
    sql = "UPDATE Request SET State = %s, Report = %s WHERE idRequest = %s"
    val = (status,report,id,)
    mycursor.execute(sql,val)

    mydb.commit()
    print("Updated request: ", id,"\n")


# BEGIN SCRIPT

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 9090))
#become a server socket
serversocket.listen(5)
print("Waiting for connections.")


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="requests"
)
print("Connected to",str(mydb))

try:
    while True:
        c, addr = serversocket.accept()
        print("New connection from",addr)
        while True:
            msgBytes = c.recv(1024)
            if not msgBytes:
                break
            else:
                message = msgBytes.decode('utf-8')
                messageParsed = parse_message(message)

                print(messageParsed.value.replace('\r','\n'))

                id = messageParsed.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.orc.orc_1.value
                worklist = messageParsed.msh.msh_10.value
                status = messageParsed.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.obx.obx_11.value
                report = messageParsed.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.obx.obx_5.value

                print(str(status))
                update_db(id,status,report)
                    
                hl7 = core.Message("ACK", validation_level=VALIDATION_LEVEL.STRICT)
                hl7.msh.msh_3 = "RequestsServer"
                hl7.msh.msh_4 = "RequestsServer"
                hl7.msh.msh_5 = "ExamsClient"
                hl7.msh.msh_6 = "ExamsClient"
                hl7.msh.msh_10 = worklist
                hl7.msh.msh_9 = "ACK"
                hl7.msh.msh_11 = "P"
                hl7.msa.msa_2 = str(id)
                hl7.msa.msa_1 = "AA"

                c.send(hl7.value.encode('utf-8'))
        c.close()

except KeyboardInterrupt:
    serversocket.shutdown(socket.SHUT_RDWR)
    serversocket.close()

