from flask_socketio import SocketIO, send, join_room, leave_room, emit
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mariaPwd#_123",
    database="Rooms"
)

cursor = conn.cursor()

app = Flask(__name__)
socketio = SocketIO(app=app)

cursor.execute("SELECT * FROM Room")
rooms = {row[0]: row[1] for row in cursor.fetchall()}

username = None

@app.route("/index")
def index():
    return render_template('index.html', rooms=rooms, user=username)

@app.route("/", methods=["GET","POST"])
def login():
    global username
    
    if request.method == "POST":

        username = request.form.get("username")

        sql = "SELECT * FROM activeusers WHERE username=%s;"
        cursor.execute(sql, (username,))
        result = cursor.fetchall()

        if len(result) > 0:
            return render_template("login.html", errormsg="That username is already in use, Try a using a different one")

        if not username or username == "":
            return "Could not get Username", 400
        
        return render_template("index.html", rooms=rooms, user=username)
    return render_template("login.html")

@app.route("/room")
def room():
    room_id = request.args.get("room_id")
    room_name = request.args.get("room_name")
    user = username

    if not room_id:
        return "no room id found", 400

    if not username:
        return "No username found", 400

    sql = "SELECT * FROM Messages WHERE room_id=%s;"
    cursor.execute(sql, (room_id,))

    messages = cursor.fetchall()

    msg_list = [msg for msg in messages]

    return render_template('room.html', messages=msg_list, room_name=room_name, room_id=room_id, username=user)

@socketio.on('room_msg')
def handle_room_msg(data):
    room_name = data.get("room_name")
    room_id = data.get("room_id")
    msg = data.get("message")
    username = data.get("username")

    if not room_id:
        return "No room id found", 400

    sql = "INSERT INTO Messages(username, room_id, content) VALUES (%s, %s, %s);"
    cursor.execute(sql, (username, room_id, msg))
    conn.commit()

    emit("msg", {"message": f"{msg}", "user":username}, room=room_id)

    print(f"Recieved and emited Msg: {username}: {msg}")

@app.route("/create_room", methods=["GET", "POST"])
def create_room():
    global rooms
    room_name = request.form.get("room_name")

    if not room_name:
        return "No room name found", 400
    
    sql = "SELECT id FROM Room WHERE room_name=%s"
    cursor.execute(sql, (room_name,))
    room_id = cursor.fetchone()

    if not room_id:         
        sql = "INSERT INTO Room(room_name) VALUES (%s)"
        cursor.execute(sql, (room_name,))

        sql = "SELECT * FROM Room"
        cursor.execute()
        rooms = {row[1]: row[0] for row in cursor.fetchall()}
        conn.commit()

    return render_template("index.html", rooms=rooms)

@socketio.on('join')
def join_chat_room(room_id) -> None:
    room_id = int(room_id)

    if room_id not in rooms:
        send("Room does not exits!")
        return

    join_room(room_id)

    send(f"{username} has joined", room=room_id)

@socketio.on('leave')
def leave_chat_room(room_id):
    room_id = int(room_id)
    leave_room(room_id)

    send(f"{username} has lefted the chat", room=room_id)

    return render_template("index.html", rooms=rooms, username=username)
    
if __name__ == '__main__':
    socketio.run(app)

