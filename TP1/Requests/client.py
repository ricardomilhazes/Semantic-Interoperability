import mysql.connector
import socket
import threading
from dateutil.parser import parse
import time

def initial_menu():
    option = input("What do you want to do? \n 1) Register new request\n 2) Consult requests\n 3) Consult report")
    execute(option)

def add_user(name,address,mobile):
    mycursor = mydb.cursor()
    
    sql = "INSERT INTO User (Name, Address, Mobile) VALUES (%s, %s, %s)"
    val = (name, address, mobile)
    mycursor.execute(sql, val)

    mydb.commit()
    print("Record inserted. ID: ", mycursor.lastrowid)

    return True

def register_user():
    name = input("Name: ")
    address = input("Address: ")
    mobile = input("Phone Number: ")

    if add_user(name,address,mobile):
        print("User registered with success.")
    else:
        print("An error ocurred, please try again.")
    initial_menu()

def user_exists(user):
    mycursor = mydb.cursor()

    sql = "SELECT * FROM User WHERE idUser = %s"
    mycursor.execute(sql,user)
    res = mycursor.fetchone()

    if res:
      return True

def add_request_db(reqType, date, user, obs):
    parsedDate = parse(date).strftime("%d/%m/%Y %H:%M")

    if not user_exists(user):
      print("User in not in our database, please insert new data: ")
      register_user()

    mycursor = mydb.cursor()

    sql_db = "INSERT INTO Pedido (State, Date, Medical_Act, User_idUser, Report, Notes) VALUES (%s, %s, %s, %s, %s, %s)"
    val = ('0', date, reqType, user, '', obs)
    mycursor.execute(sql_db, val)

    mydb.commit()
    print("Record inserted. ID: ", mycursor.lastrowid)

    return True

def register_request():
    reqType = input("Medical_Act: ")
    date = input("Date (DD/MM/YYYY HH:MM): ")
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

def consult_report(request):
    mycursor = mydb.cursor()

    sql = "SELECT Report FROM Request WHERE idRequest = %s"
    mycursor.execute(sql,request)
    res = mycursor.fetchone()

    print("Report: ", res)
    initial_menu()

def execute(option):
    if option == "1":
        register_request()
    elif option == "2":
        consult_request()
    elif option == "3":
        consult_report()
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


# BEGIN SCRIPT

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