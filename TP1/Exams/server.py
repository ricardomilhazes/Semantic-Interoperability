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
    mycursor.execute(sql,id)
    print("pedido "+ str(id) +" removido da worklist")
    mydb.commit()

def update_db(idExam, status, date, medical_act, idUser, name, idProcess, address, mobile, notes, report):
    mycursor=mydb.cursor()

    sql = "IF EXISTS (SELECT * FROM User WHERE idUser = %s) UPDATE User SET Name = %s, idProcess = %s, Address = %s, Mobile = %s ELSE INSERT INTO User VALUES(%s,%s,%s,%s)"
    val = (idUser,name,idProcess,address,mobile,name,idProcess,address,mobile)
    mycursor.execute(sql,val)

    sql2 = "INSERT INTO Exam VALUES (%s,%s,%s,%s,%s,%s,%s)"
    val2 = (idExam,status,date,medical_act,idUser,report,notes)
    mycursor.execute(sql2,val2)

    mydb.commit()


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
        id = message.ORM_O01_ORDER.ORC.orc_2.value
        status = message.ORM_O01_ORDER.orc.orc_1.value
        date = message.ORM_O01_ORDER.ORC.orc_10.value
        medical_act = message.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.OBR.obr_4.value
        idUser = message.ORM_O01_PATIENT.pid.pid_2.value
        name = message.ORM_O01_PATIENT.pid.pid_3.value
        idProcess = message.ORM_O01_PATIENT.pid.pid_5.value
        address = message.ORM_O01_PATIENT.pid.pid_11.value
        mobile = message.ORM_O01_PATIENT.pid.pid_13.value
        notes = message.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.OBR.obr_13.value
        report = message.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.OBR.obr_12.value
        update_db(id,status,report,medical_act,idUser,name,idProcess,address,mobile,notes,report)
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
        s.send(hl7)
