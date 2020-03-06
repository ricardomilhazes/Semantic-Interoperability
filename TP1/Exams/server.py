# Two threads: 
# 1 - for receiving messages or ACKs from the other machine's server and writing them to the DB
# 2 - for listening to the worklist and sending messages with the Exams reports and/or its state update

import socket
import mysql.connector
from hl7apy import core
from hl7apy.consts import VALIDATION_LEVEL
from hl7apy.parser import parse_message, parse_field

def get_id_from_msg():
    return 0

def remove_from_wl(id):
    mycursor=mydb.cursor()
    sql="DELETE FROM Worklist WHERE idWorkList=%s"    
    mycursor.execute(sql,(id,))
    print("pedido "+ str(id) +" removido da worklist")
    mydb.commit()

def update_db(idExam, status, date, medical_act, idUser, name, idProcess, address, mobile, notes, report):
    mycursor=mydb.cursor()

    sql = "INSERT INTO User (idUser,Name,idProcess,Address,Mobile) VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE Name = %s, idProcess = %s, Address = %s, Mobile = %s"
    val = (idUser,name,idProcess,address,mobile,name,idProcess,address,mobile)
    mycursor.execute(sql,val)

    sql2 = "INSERT INTO Exam (idRequest,State,Date,Medical_Act,User_idUser,Report,Notes) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    val2 = (idExam,status,date,medical_act,idUser,report,notes)
    mycursor.execute(sql2,val2)

    mydb.commit()


# BEGIN SCRIPT

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 9999))
#become a server socket
serversocket.listen(5)
print("Waiting for connections.")

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="exams"
)
print("Connected to",str(mydb))

while True:
    c, addr = serversocket.accept()
    print("New connection from",addr)
    msgBytes = c.recv(1024)
    message = msgBytes.decode('utf-8')
    messageParsed = parse_message(message)
    if parse_field(message,"MSH_9").to_er7() == "ACK":
        id = messageParsed.msh.msh_10.value
        remove_from_wl(id)
    else:
        id = messageParsed.ORM_O01_ORDER.ORC.orc_2.value
        status = messageParsed.ORM_O01_ORDER.orc.orc_1.value
        date = messageParsed.ORM_O01_ORDER.ORC.orc_10.value
        medical_act = messageParsed.nte.nte_4.value
        idUser = messageParsed.ORM_O01_PATIENT.pid.pid_2.value
        name = messageParsed.ORM_O01_PATIENT.pid.pid_3.value
        idProcess = messageParsed.ORM_O01_PATIENT.pid.pid_5.value
        address = messageParsed.ORM_O01_PATIENT.pid.pid_11.value
        mobile = messageParsed.ORM_O01_PATIENT.pid.pid_13.value
        notes = messageParsed.ORM_O01_PATIENT.nte.nte_3.value
        report = messageParsed.nte.nte_3.value

        # update database
        update_db(id,status,date,medical_act,idUser,name,idProcess,address,mobile,notes,report)

        # send ack
        hl7 = core.Message("ACK", validation_level=VALIDATION_LEVEL.STRICT)
        hl7.msh.msh_3 = "PedidosServer"
        hl7.msh.msh_4 = "PedidosServer"
        hl7.msh.msh_5 = "ExamesServer"
        hl7.msh.msh_6 = "ExamesServer"
        hl7.msh.msh_10 = str(id)
        hl7.msh.msh_9 = "ACK"
        hl7.msh.msh_11 = "P"
        hl7.msa.msa_2 = str(id)
        hl7.msa.msa_1 = "AA"
        c.send(hl7.value.encode('utf-8'))
