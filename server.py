from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO,leave_room,join_room,send
from flask_cors import CORS
from string import ascii_uppercase
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)

socketio = SocketIO(app, cors_allowed_origins='*')
rooms = {}


def generate_unique_code(n):
    while True:
        code = ""
        for _ in range(n):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code


@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        print("post request")
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        if not name:
            return render_template("index.html", error="please enter name", code=code, name=name)

        if join != False and not code:
            return render_template("index.html", error="please enter a valid room id", code=code, name=name)

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}

        elif code not in rooms:
            return redirect(url_for("home", error="room doesnt exist", code=code, name=name))

        session['room'] = room
        session['name'] = name
        return redirect(url_for("room"))

    return render_template("index.html")


@app.route("/room")
def room():
    room= session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return(url_for("home"))
    return render_template('chat.html')


@socketio.on('connect')
def show(data):
    room=session.get('room')
    name=session.get('name')

    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)
    send({"name":name,"message":"has entered the room"},to=room)
    rooms[room]["members"]+=1
    
    print('-----')
    print(room,name)
    print('-----')
    return

@socketio.on('my event')
def sqhow(data):
    print('-----')
    print(data)
    print('-----')
    return


if __name__ == '__main__':
    socketio.run(app, debug=False)
    # host='0.0.0.0', port=5000
