# Server UI - Machine B

import mysql.connector
import socket
import threading
from hl7apy import core
from hl7apy.consts import VALIDATION_LEVEL
from dateutil.parser import parse
import time


def initial_menu():
    option = input("What do you want to do? \n 1) Issue Report\n 2) Perform Exam\n 3) Consult Requests")
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
  mycursor = mydb.cursor()

  sql = "SELECT * FROM Exam"
  mycursor.execute(sql)
  res = mycursor.fetchall()

  print("ID | State | Date")
  for request in res:
    print(request[0], "|", request[1], "|", request[2])
  initial_menu()

def change_request_state(request):
    mycursor = mydb.cursor()

    sql = "UPDATE Exam SET State = '1' WHERE idRequest = %s"
    mycursor.execute(sql,(request,))

    mydb.commit()
    print("Exam performed. ID: ", mycursor.lastrowid)

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

    # PV1
    hl7.ORM_O01_PATIENT.add_group("ORM_O01_PATIENT_VISIT")
    hl7.ORM_O01_PATIENT.ORM_O01_PATIENT_VISIT.add_segment("PV1")
    hl7.ORM_O01_PATIENT.ORM_O01_PATIENT_VISIT.PV1.pv1_1 = "1"
    hl7.ORM_O01_PATIENT.ORM_O01_PATIENT_VISIT.PV1.pv1_2 = "1"

    # ORC
    if request[2] == '-1':
        hl7.ORM_O01_ORDER.orc.orc_1 = '-1'
    else:
        hl7.ORM_O01_ORDER.orc.orc_1 = '0'
        hl7.ORM_O01_ORDER.ORC.orc_10 = request[3].strftime("%Y-%m-%d")
        hl7.ORM_O01_ORDER.ORC.orc_2 = str(request[1])

    # OBR
    hl7.ORM_O01_ORDER.add_group("ORM_O01_ORDER_DETAIL")
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.add_segment("ORM_O01_ORDER_CHOICE")
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.add_segment("OBR")
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.OBR.obr_13 = request[10]
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.OBR.obr_12 = request[11]
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.OBR.obr_4 = request[4]
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.add_segment("RQD")
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.add_segment("RQ1")
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.add_segment("RXO")
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.add_segment("ODS")
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.add_segment("ODT")

    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.ODS.ods_1 = ""
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.ODS.ods_3 = ""
    hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_ORDER_CHOICE.ODT.odt_1 = ""

    assert hl7.validate() is True
    print(str(hl7.value))

    return hl7.value

# THREAD FUNC: contiuously reading from Worklist table and sending new requests
def worklist_listener():
    last_row = 0
    while True:
        # read rows from worklist every 2 mins
        time.sleep(120)
        mycursor = mydb.cursor()
        getNewRows = "SELECT * FROM Worklist WHERE id > %s"
        mycursor.execute(getNewRows,last_row)
        res = mycursor.fetchall()
        for request in res:
            #user = fetch_user(id)
            hl7msg = create_HL7_msg(request)
            s.send(hl7msg)
        last_row = mycursor.lastrowid

#BEGIN SCRIPT

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'
port = 9090
s.connect((host,port))

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  passwd="",
  database="exams"
)
if mydb:
    print(" Connected to " + str(mydb))
    wlThread = threading.Thread(target=worklist_listener)
    wlThread.start()
    print("Welcome to the Requests UI!")
    initial_menu()