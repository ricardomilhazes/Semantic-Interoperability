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
    option = input("What do you want to do? \n 1) Issue Report\n 2) Perform Exam\n 3) Consult Requests\n 4) Cancel Exam\n OPTION: ")
    execute(option)

def add_report(request,report):
    
    mycursor = mydb.cursor()

    sql = "UPDATE Exam SET Report = %s, State = '2' WHERE idRequest = %s"
    mycursor.execute(sql,(report,request,))

    mydb.commit()
    
    print("Report added. ID: ", mycursor.lastrowid,"\n")

    return True

def register_report():
    request = input("Which request you wish to add a report (ID) to: ")
    report = input("Write your report: ")

    if add_report(request,report):
        print("Report added with success. \n")
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

def change_request_state(request,state):
    
    mycursor = mydb.cursor()

    sql = "UPDATE Exam SET State = %s WHERE idRequest = %s"
    mycursor.execute(sql,(state, request))

    mydb.commit()
    print("Exam performed with success. \n")
    
    return True

def perform_exam():
    request = input("Which request you wish to perform an exam on: ")

    if change_request_state(request):
        print("Exam performed with success \n")

    else:
        print("An error ocurred, please try again.")
    initial_menu()

def cancel_exam():
    request = input("Which exam you wish to cancel: ")

    if change_request_state(request, 3):
        print("Exam canceled with success")
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
    elif option == "4":
        cancel_exam()
    else:
        print("Wrong input. Please try again.\n")
        initial_menu()

# get user from DB with the given ID
# def fetch_user(id):
#    return id

# create msg with HL7 format
def create_HL7_msg(request):
    
    # Create Message
    hl7 = core.Message("ORU_R01", validation_level=VALIDATION_LEVEL.STRICT)

    # Message Header
    hl7.msh.msh_3 = "ExamsClient"
    hl7.msh.msh_4 = "ExamsClient"
    hl7.msh.msh_5 = "RequestsServer"
    hl7.msh.msh_6 = "RequestsServer"
    hl7.msh.msh_9 = "ORU^R01^ORU_R01"
    hl7.msh.msh_10 = str(request[0])
    hl7.msh.msh_11 = "P"

    # PID
    hl7.add_group("ORU_R01_PATIENT_RESULT")
    hl7.ORU_R01_PATIENT_RESULT.add_group("ORU_R01_PATIENT")
    hl7.ORU_R01_PATIENT_RESULT.ORU_R01_PATIENT.pid.pid_3 = str(request[5])
    hl7.ORU_R01_PATIENT_RESULT.ORU_R01_PATIENT.pid.pid_5 = str(request[6])
    hl7.ORU_R01_PATIENT_RESULT.ORU_R01_PATIENT.pid.pid_18 = str(request[7])
    hl7.ORU_R01_PATIENT_RESULT.ORU_R01_PATIENT.pid.pid_11 = str(request[8])
    hl7.ORU_R01_PATIENT_RESULT.ORU_R01_PATIENT.pid.pid_13 = str(request[9])

    # ORC
    hl7.ORU_R01_PATIENT_RESULT.add_group("ORU_R01_ORDER_OBSERVATION")
    hl7.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.orc.orc_10 = request[3].strftime("%Y-%m-%d")
    hl7.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.orc.orc_1 = str(request[1])

    # OBR
    hl7.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.obr.obr_4 = str(request[4])

    # OBX
    hl7.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.add_group("ORU_R01_OBSERVATION")
    hl7.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.obx.obx_5 = str(request[11])
    hl7.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.obx.obx_11 = str(request[2]) 
    hl7.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.obx.obx_3 = str(request[10])


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
    print("Request "+ str(id) +" removed from worklist\n")
    mydb.commit()
    

def ack_listener():
    while True:
        msgBytes = s.recv(1024)
        message = msgBytes.decode('utf-8')
        try:
            messageParsed = parse_message(message)
            print("\nACK RECEIVED")
            print(messageParsed.value.replace('\r','\n'))

            if messageParsed.msh.msh_9.value == "ACK":
                id = int(messageParsed.msh.msh_10.value)
                remove_from_wl(id)
        except:
            print("\nreceived:",message)


#BEGIN SCRIPT

def init_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
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
        passwd="",
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