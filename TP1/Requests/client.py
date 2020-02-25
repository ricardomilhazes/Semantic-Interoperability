import mysql.connector
import socket
import threading
from dateutil.parser import parse
import time

def initial_menu():
    option = input("What do you want to do? \n 1) Register new user \n 2) Consult users \n 3) Register new request\n")
    execute(option)

def add_user(name,address,phone):
    mycursor = mydb.cursor()
    # idProcesso ??? 
    sql = "INSERT INTO Utente (nome, morada, telefone) VALUES (%s, %s, %s)"
    val = (name, address, phone)
    mycursor.execute(sql, val)

    mydb.commit()
    print("Record inserted. ID: ", mycursor.lastrowid)

    return True

def register_user():
    name = input("Name: ")
    address = input("Address: ")
    phone = input("Phone Number: ")
    if add_user(name,address,phone):
        print("User registered with success.")
    else:
        print("An error ocurred, please try again.")
    initial_menu()

def consult_users():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM Utente")
    res = mycursor.fetchall()

    print("ID | Name | Address | Phone Number")
    for user in res:
        print(user[0], "|", user[1], "|", user[2], "|", user[3])

    initial_menu()

def add_request_db(reqType, date, user, episode, obs):
    parsedDate = parse(date).strftime("%d/%m/%Y %H:%M")

    mycursor = mydb.cursor()
    sql_db = "INSERT INTO Pedido (tipo, episodio, data, relatorio, estado, obs, idutente) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (reqType, episode, parsedDate, '', '0', obs, user)
    mycursor.execute(sql_db, val)
    mydb.commit()
    print("Record inserted. ID: ", mycursor.lastrowid)

    sql_worklist = "INSERT INTO Worklist (tipo, episodio, data, relatorio, estado, obs, idutente) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    mycursor.execute(sql_worklist, val)
    mydb.commit()
    print("Record inserted. ID: ", mycursor.lastrowid)

    return True

def register_request():
    reqType = input("Type: ")
    date = input("Date (DD/MM/YYYY HH:MM): ")
    user = input("User: ")
    episode = input("Episode: ")
    obs = input("Obs: ")
    if add_request_db(reqType, date, user, episode, obs):
            print("Request registered with success.")
    initial_menu()

def execute(option):
    if option == "1":
        register_user()
    elif option == "2":
        consult_users()
    elif option == "3":
        register_request()
    else:
        print("Wrong input. Please try again.\n")
        initial_menu()

def fetch_user(id):
    return id

def create_HL7_msg(request,user):
    return "Msg"

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
           

s = socket.socket()
host = socket.gethostname()
port = 9999
s.bind(host,port)

mydb = mysql.connector.connect(
  host="localhost",
  user="yourusername",
  passwd="yourpassword",
  database="NOME_DA_DB"
)
if mydb:
    print(" Connected to " + mydb)
    wlThread = threading.Thread(target=worklist_listener)
    print("Welcome to the Requests UI!")
    initial_menu()