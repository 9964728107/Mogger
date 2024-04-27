from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

import asyncio
import re
import json
import google.generativeai as genai
from google.generativeai import GenerativeModel
from pdfminer.high_level import extract_text


app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)

rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")


GOOGLE_API_KEY = "AIzaSyAr6G0NZg0-d75x5LeuoUXpCN1Xu6DcV7A"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

async def save_pdf(filename, pdf_file):
    with open(f'uploads/{filename}', 'wb') as f:
        pdf_file.save(f)

@app.route("/mcqs", methods=['POST'])
async def deal():
    pdf_file = request.files['pdf_file']
    filename = pdf_file.filename
    await save_pdf(filename, pdf_file)
    await asyncio.sleep(1)
    text = extract_text(f'uploads/{filename}')
    response = model.generate_content(f"For the given data, generate 5 multiple-choice questions based on the content of the PDF. Provide the questions and answer options in raw JSON format. Each question should include the question text and four options. The data to be used for generating questions is as follows: {text} \n\nSample JSON format:\n```json\n{{ 'questions': [ {{'question': 'What is the capital of France?', 'options': ['London', 'Paris', 'Berlin', 'Rome'],'answer':'answer'}}, {{'question': 'Who wrote \'Romeo and Juliet\'?', 'options': ['William Shakespeare', 'Jane Austen', 'Charles Dickens', 'Leo Tolstoy'],'answer':'answer'}}, {{'question': 'What is the chemical symbol for water?', 'options': ['O2', 'H2O', 'CO2', 'NaCl'],'answer':'answer'}} ] }}\n```")
    response = json.loads(re.sub(r'^```json\s+|```$', '', response.text))
    return render_template("chat.html", data=text, response=response['questions'], load=False)

@app.route("/mcqs", methods=['GET'])
def dipl():
    return render_template("chat.html", data="", response="yet to cook", load=True)




if __name__ == "__main__":
    socketio.run(app, debug=True)