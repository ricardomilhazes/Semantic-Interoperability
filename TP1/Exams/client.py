# Server UI - Machine B

import mysql.connector
import socket
import threading
from dateutil.parser import parse
import time


def initial_menu():
    option = input("What do you want to do? \n 1) Issue Report\n 2) Perform Exam\n 3) Consult Requests")
    execute(option)

def add_report(request,report):
    mycursor = mydb.cursor()

    sql = "UPDATE Exam SET Report = %s, State = '2' WHERE idRequest = %s"
    mycursor.execute(sql,report,request)

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
    mycursor.execute(sql,request)

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
def fetch_user(id):
    return id

# create msg with HL7 format
def create_HL7_msg(request,user):
    return "Msg"

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
            user = fetch_user(id)
            hl7msg = create_HL7_msg(request,user)
            s.send(hl7msg)
        last_row = mycursor.lastrowid

#BEGIN SCRIPT

s = socket.socket()
host = socket.gethostname()
port = 9999
s.bind((host,port))

mydb = mysql.connector.connect(
  host="Hostname",
  user="Username",
  passwd="Password",
  database="DB_Name"
)
if mydb:
    print(" Connected to " + str(mydb))
    wlThread = threading.Thread(target=worklist_listener)
    print("Welcome to the Requests UI!")
    initial_menu()