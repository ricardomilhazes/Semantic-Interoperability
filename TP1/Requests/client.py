import mysql.connector
import socket
import threading
from hl7apy import core
from hl7apy.consts import VALIDATION_LEVEL
from dateutil.parser import parse
import time

def initial_menu():
    option = input("What do you want to do? \n 1) Register new request\n 2) Consult requests\n 3) Consult report")
    execute(option)

def add_user(name,address,mobile,idProcess):
    mycursor = mydb.cursor()
    
    sql = "INSERT INTO User (Name, Address, Mobile,idProcess) VALUES (%s, %s, %s,%s)"
    val = (name, address, mobile,idProcess,)
    mycursor.execute(sql, val)

    mydb.commit()
    print("Record inserted. ID: ", mycursor.lastrowid)

    return True, mycursor.lastrowid

def register_user():
    name = input("Name: ")
    address = input("Address: ")
    mobile = input("Phone Number: ")
    idProcess = input("Process ID: ")

    res, id = add_user(name, address, mobile,idProcess)

    if res:
        print("User registered with success.")
        return id

    else:
        print("An error ocurred, please try again.")
    initial_menu()

def user_exists(user):
    mycursor = mydb.cursor()

    sql = "SELECT * FROM User WHERE idUser = %s"
    mycursor.execute(sql,(user,))
    res = mycursor.fetchone()

    if res:
      return True

def add_request_db(reqType, date, user, obs):

    if not user_exists(user):
      print("User in not in our database, please insert new data: ")
      user = register_user()

    parsedDate = parse(date).strftime("%Y-%m-%d %H:%M:%S")

    mycursor = mydb.cursor()

    sql_db = "INSERT INTO Request VALUES (%s,%s, %s, %s, %s, %s,%s)"
    val = (None,'0', parsedDate, reqType, user,'',obs,)
    mycursor.execute(sql_db, val)

    mydb.commit()
    print("Record inserted. ID: ", mycursor.lastrowid)

    return True

def register_request():
    reqType = input("Medical_Act: ")
    date = input("Date (YYYY-MM-DD HH:MM): ")
    user = input("User: ")
    obs = input("Notes: ")

    if add_request_db(reqType, date, user, obs):
            print("Request registered with success.")
    initial_menu()

def consult_requests():
    mycursor = mydb.cursor()

    sql = "SELECT * FROM Request"
    mycursor.execute(sql)
    res = mycursor.fetchall()
  
    print("ID | State | Date")
    for request in res:
        print(request[0], "|", request[1], "|", request[2])
    initial_menu()

def consult_report():
    request = input("Which request you wish do see report: ")

    mycursor = mydb.cursor()

    sql = "SELECT Report FROM Request WHERE idRequest = %s"
    mycursor.execute(sql,(request,))
    res = mycursor.fetchone()

    print("Report: ", res)
    initial_menu()

def execute(option):
    if option == "1":
        register_request()
    elif option == "2":
        consult_requests()
    elif option == "3":
        consult_report()
    else:
        print("Wrong input. Please try again.\n")
        initial_menu()

# get user from DB with the given ID
def fetch_user(id):
    mycursor = mydb.cursor()

    sql = "SELECT * FROM User WHERE idUser = %s"
    mycursor.execute(sql,(id,))
    res = mycursor.fetchone()

    return res

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
    if request[2] == '-1':
        hl7.ORM_O01_ORDER.orc.orc_1 = '-1'
    else:
        hl7.ORM_O01_ORDER.orc.orc_1 = '0'
        hl7.ORM_O01_ORDER.ORC.orc_10 = request[3].strftime("%Y-%m-%d")
        hl7.ORM_O01_ORDER.ORC.orc_2 = str(request[1])

    # NTE
    hl7.nte.nte_3 = str(request[11])
    hl7.nte.nte_4 = str(request[4])

    assert hl7.validate() is True

    return hl7.value
    
# THREAD FUNC: contiuously reading from Worklist table and sending new requests
def worklist_listener():
    last_row = 0
    while True:
        # read rows from worklist every 2 mins
        time.sleep(5)
        mycursor = mydb.cursor()
        getNewRows = "SELECT * FROM Worklist WHERE idWorkList > %s"
        mycursor.execute(getNewRows,(last_row,))
        res = mycursor.fetchall()
        for request in res:
            hl7msg = create_HL7_msg(request)
            print(hl7msg.replace('\r','\n'))
            s.send(hl7msg.encode('utf-8'))
        last_row = mycursor.lastrowid


# BEGIN SCRIPT

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# exams server host and port:
host = 'localhost'
port = 9999
s.connect((host,port))

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="requests"
)
if mydb:
    print(" Connected to " + str(mydb))
    wlThread = threading.Thread(target=worklist_listener)
    wlThread.start()
    print("Welcome to the Requests UI!")
    initial_menu()