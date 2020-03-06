# Server UI - Machine B

import mysql.connector
import socket
import threading
from hl7apy import core
from hl7apy.consts import VALIDATION_LEVEL
from hl7apy.parser import parse_message, parse_field
from dateutil.parser import parse
import time


def initial_menu():
    option = input("What do you want to do? \n 1) Issue Report\n 2) Perform Exam\n 3) Consult Requests\nOPTION: ")
    execute(option)

def add_report(request,report):
    
    mycursor = mydb.cursor()

    sql = "UPDATE Exam SET Report = %s, State = '2' WHERE idRequest = %s"
    mycursor.execute(sql,(report,request,))

    mydb.commit()
    
    print("Report added. ID: ", mycursor.lastrowid)

    return True

def register_report():
    request = input("Which request you wish to add a report (ID) to: ")
    report = input("Write your report: ")

    if add_report(request,report):
        print("Report added with success.")
    else:
        print("An error ocurred, please try again.")
    initial_menu()

def consult_requests():
    db = init_db()
    mycursor = db.cursor()

    sql = "SELECT * FROM Exam"
    mycursor.execute(sql)
    res = mycursor.fetchall()

    print("ID | State | Date")
    for request in res:
        print(request[0], "|", request[1], "|", request[2])
    
    db.close()
    initial_menu()

def change_request_state(request):
    
    mycursor = mydb.cursor()

    sql = "UPDATE Exam SET State = '1' WHERE idRequest = %s"
    mycursor.execute(sql,(request,))

    mydb.commit()
    print("Exam performed with success.")
    

    return True

def perform_exam():
    request = input("Which request you wish to perform an exam on: ")

    if change_request_state(request):
        print("Exam performed with success")
    else:
        print("An error ocurred, please try again.")
    initial_menu()

def execute(option):
    if option == "1":
        register_report()
    elif option == "2":
        perform_exam()
    elif option == "3":
        consult_requests()
    else:
        print("Wrong input. Please try again.\n")
        initial_menu()

# get user from DB with the given ID
# def fetch_user(id):
#    return id

# create msg with HL7 format
def create_HL7_msg(request):
    
    # Create Message
    hl7 = core.Message("ORM_O01", validation_level=VALIDATION_LEVEL.STRICT)

    # Message Header
    hl7.msh.msh_3 = "PedidosClient"
    hl7.msh.msh_4 = "PedidosClient"
    hl7.msh.msh_5 = "ExamesServer"
    hl7.msh.msh_6 = "ExamesServer"
    hl7.msh.msh_9 = "ORM^O01^ORM_O01"
    hl7.msh.msh_10 = str(request[0])
    hl7.msh.msh_11 = "P"

    # PID
    hl7.add_group("ORM_O01_PATIENT")
    hl7.ORM_O01_PATIENT.pid.pid_2 = str(request[5])
    hl7.ORM_O01_PATIENT.pid.pid_3 = str(request[6])
    hl7.ORM_O01_PATIENT.pid.pid_5 = str(request[7])
    hl7.ORM_O01_PATIENT.pid.pid_11 = str(request[8])
    hl7.ORM_O01_PATIENT.pid.pid_13 = str(request[9])
    hl7.ORM_O01_PATIENT.nte.nte_3 = str(request[10])

    # PV1
    hl7.ORM_O01_PATIENT.add_group("ORM_O01_PATIENT_VISIT")
    hl7.ORM_O01_PATIENT.ORM_O01_PATIENT_VISIT.add_segment("PV1")
    hl7.ORM_O01_PATIENT.ORM_O01_PATIENT_VISIT.PV1.pv1_1 = "1"
    hl7.ORM_O01_PATIENT.ORM_O01_PATIENT_VISIT.PV1.pv1_2 = "1"

    # ORC

    hl7.ORM_O01_ORDER.orc.orc_1 = request[2]
    hl7.ORM_O01_ORDER.ORC.orc_10 = request[3].strftime("%Y-%m-%d")
    hl7.ORM_O01_ORDER.ORC.orc_2 = str(request[1])

    # NTE
    hl7.nte.nte_3 = str(request[11])
    hl7.nte.nte_4 = str(request[4])

    assert hl7.validate() is True
    # print(str(hl7.value))

    return hl7.value

# THREAD FUNC: contiuously reading from Worklist table and sending new requests
def worklist_listener():
    
    while True:
        # read rows from worklist every 5secs
        time.sleep(5)
        mycursor = mydb.cursor()
        getNewRows = "SELECT * FROM Worklist"
        mycursor.execute(getNewRows)
        res = mycursor.fetchall()
        for request in res:
            #user = fetch_user(id)
            hl7msg = create_HL7_msg(request)
            s.send(hl7msg.encode('utf-8'))
    

def remove_from_wl(id):
    
    mycursor=mydb.cursor()
    sql="DELETE FROM Worklist WHERE idWorkList=%s"    
    mycursor.execute(sql,(id,))
    print("Request "+ str(id) +" removed from worklist")
    mydb.commit()
    

def ack_listener():
    while True:
        msgBytes = s.recv(1024)
        message = msgBytes.decode('utf-8')
        try:
            messageParsed = parse_message(message)
            if messageParsed.msh.msh_9.value == "ACK":
                id = int(messageParsed.msh.msh_10.value)
                remove_from_wl(id)
        except:
            print("received:",message)


#BEGIN SCRIPT

def init_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Hmpp1998",
        database="exams"
    )
    return db

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'
port = 9090
s.connect((host,port))

mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Hmpp1998",
        database="exams"
)

wlThread = threading.Thread(target=worklist_listener)
wlThread.setDaemon(True)
wlThread.start()
ackThread = threading.Thread(target=ack_listener)
ackThread.setDaemon(True)
ackThread.start()
print("Welcome to the Requests UI!")
initial_menu()