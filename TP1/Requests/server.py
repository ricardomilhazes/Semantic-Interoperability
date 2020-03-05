# For receiving ACKs and request updates from the other machine's server and then clearing the worklist

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
    
    mydb.commit()
    print("pedido "+ str(id) +" removido da worklist")

def update_db(id, status, report):
    mycursor = mydb.cursor()
    
    sql = "UPDATE Request SET State = %s, Report = %s WHERE idRequest = %s"
    val = (status,report,id,)
    mycursor.execute(sql,val)

    mydb.commit()
    print("Updated request: ", id)


# BEGIN SCRIPT
s = socket.socket()
host = socket.gethostname()
port = 9090
s.bind((host,port))

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  passwd="",
  database="requests"
)

# wait for connections
s.listen()

while True:
    ids = []
    c, addr = s.accept()
    msgBytes = c.recv(1024)
    message = parse_message(msgBytes)
    if parse_field(msgBytes,"MSH_9").to_er7() == "ACK":
        id = parse_field(msgBytes,"MSH_10").to_er7()
        remove_from_wl(id)
    else:
        id = message.ORM_O01_ORDER.ORC.orc_2.value
        status = message.ORM_O01_ORDER.orc.orc_1.value
        report = message.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.OBR.obr_12.value
        update_db(id,status,report)
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


