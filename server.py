from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
import time
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
mcqs={}

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
            rooms[room] = {"members": 0, "scores": [],"mcqs":[],"names":[]}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("dipl"))

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
    #adding members in the list
    if name not in rooms[room]['names']:
      rooms[room]["names"].append(name)

    socketio.emit('members',rooms[room]["names"],to=room)
    # elif name in rooms[room]['names']:
    #   socketio.emit('members',rooms[room]["names"],to=room)

    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")
    print(rooms)

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


GOOGLE_API_KEY = ""
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

async def save_pdf(filename, pdf_file):
    with open(f'uploads/{filename}', 'wb') as f:
        pdf_file.save(f)

# @app.route("/mcqs", methods=['POST'])
# async def deal():
    

@app.route("/mcqs",methods=["GET","POST"])
def dipl():
     if request.method == "GET":
        room = session.get("room")
        if room is None or session.get("name") is None or room not in rooms:
            return redirect(url_for("home"))

        #  return render_template("room.html", code=room, messages=rooms[room]["messages"])
        return render_template("chat.html", data="",code=room, response="", load=True)
     if request.method == "POST":
            room = session.get("room")
            if "room" not in session or "name" not in session:
                    session.clear()
                    return redirect(url_for("home"))
            room = session["room"]
            name = session["name"]
            # pdf_file = request.files['pdf_file']
            # filename = pdf_file.filename
            # await save_pdf(filename, pdf_file)
            # await asyncio.sleep(1)
            # text = extract_text(f'uploads/{filename}')
            # response = model.generate_content(f"For the given data, generate 5 multiple-choice questions based on the content of the PDF. Provide the questions and answer options in raw JSON format. Each question should include the question text and four options. The data to be used for generating questions is as follows: {text} \n\nSample JSON format:\n```json\n{{ 'questions': [ {{'question': 'What is the capital of France?', 'options': ['London', 'Paris', 'Berlin', 'Rome'],'answer':'answer'}}, {{'question': 'Who wrote \'Romeo and Juliet\'?', 'options': ['William Shakespeare', 'Jane Austen', 'Charles Dickens', 'Leo Tolstoy'],'answer':'answer'}}, {{'question': 'What is the chemical symbol for water?', 'options': ['O2', 'H2O', 'CO2', 'NaCl'],'answer':'answer'}} ] }}\n```")
            response='''[
            {
                "question": "What is the primary goal of data science?",
                "options": [
                "To collect and store vast amounts of data",
                "To derive meaningful insights and information from data",
                "To develop and implement machine learning models",
                "To create visualizations and dashboards"
                ],
                "answer": "To derive meaningful insights and information from data"
            },
            {
                "question": "Which of the following is NOT a stage in the data science life cycle?",
                "options": [
                "Data collection",
                "Data analysis",
                "Model evaluation",
                "Model development"
                ],
                "answer": "Model development"
            },
            {
                "question": "What is the role of a data scientist in a data science project?",
                "options": [
                "To analyze data and extract insights",
                "To develop machine learning models",
                "To communicate findings to stakeholders",
                "All of the above"
                ],
                "answer": "All of the above"
            },
            {
                "question": "Which of the following industries is NOT commonly associated with the application of data science?",
                "options": [
                "Healthcare",
                "Finance",
                "Manufacturing",
                "Education"
                ],
                "answer": "Education"
            },
            {
                "question": "What is the key benefit of using data science in business decision-making?",
                "options": [
                "Increased efficiency and productivity",
                "Improved customer insights",
                "Optimized resource allocation",
                "All of the above"
                ],
                "answer": "All of the above"
            }
            ]'''

            # response = json.loads(re.sub(r'^```json\s+|```$', '', response.text))
            response=json.loads(response)
            answers = list(map(lambda x: x['answer'], response))
            print(answers)
            print("-----")
            print(response)
            print("-----")
            print(room)
            
            rooms[room]["mcqs"].append(response)
            # rooms[room]["scores"].append(content) 

            try:
                socketio.emit("response", response, room=room)
                print(f"Emitted response object to room {room}")
            except Exception as e:
                print(f"Error emitting response object: {e}")


            # return render_template("chat.html", data="text", response=response['questions'], load=False)
            return render_template("chat.html", data="text",code=room, response=response, load=False, answers=answers)
            # return redirect(url_for("dipl"))

async def timer(data,room):
    count = data
    while count > 0:
        print(count)
        await asyncio.sleep(1)
        socketio.emit("timer",count,to=room)    
        count -= 1
    print("time over")
    socketio.emit("timer",count,to=room)

@socketio.on("initiateTimer")
def initiateTimer(data):
 room= session["room"]
 asyncio.run(timer(data,room))
 
            
@socketio.on("paris")
def paris(string):
    print(string)
    room=session["room"]
    print("room",room)
    socketio.emit('Paris', "morning", room=room)


@socketio.on("varify")
def varify(data):
    room=session["room"]
    if room not in rooms:
        print("room was not there!")
       
     
    print(type(data))
    choices = data['choices']
    answers = data['answers']

    print("Choices:", choices)
    print("Answers:", answers)
    # Preprocess choices and answers
    choices = [choice.strip().lower() for choice in choices]
    answers = [answer.strip().lower() for answer in answers]
    print("Choices:", choices)
    print("Answers:", answers)

    result = list(map(lambda x, y: x == y, choices, answers))
    points=0
    for res in result:
        if res:
            points=points+1
        if not res:
            points=points+0

    print("Result:", result)
    print('points',points)

    socketio.emit("update_points", points) 


    content={
        "name": session["name"],
        "score": points
    }     
     
    rooms[room]["scores"].append(content) 
      
    #send(rooms[room]['scores'], to=room)
    socketio.emit('varify',rooms[room]['scores'],to=room)#, room=room
    print(content)
    # rooms[room]["messages"].append(content)
    print(f"{session.get('name')} scored: {content['score']}")

    
    
    

    # Compare choices with answers
   


    
   



if __name__ == "__main__":
    socketio.run(app, debug=True)