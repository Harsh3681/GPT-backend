from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
import openai
import os
from flask_cors import CORS

openai.api_key = os.environ.get('OPENAI_SECRET')

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin:admin@cluster0.5rzjxal.mongodb.net/DBGPT"
mongo = PyMongo(app)

@app.route("/")
def home():
    chats = mongo.db.chats.find({})
    myChats = [chat for chat in chats]
    print(myChats)
    return render_template("index.html", myChats=myChats)



@app.route("/api", methods=["GET", "POST"])
def qa():
    if request.method == "POST":
        print(request.json)
        question = request.json.get("question")
        question_lowercase = question.lower()  # Convert question to lowercase

        chat = mongo.db.chats.find_one({"question": question_lowercase})
        print(chat)
        if chat:
            data = {"question": question, "answer": f"{chat['answer']}"}
            return jsonify(data)
        else:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=question,
                temperature=0.7,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            print(response)
            # data = {"result": f"Answer of {question}"}
            data = {"question": question, "answer": response["choices"][0]["text"]}

            # Store the question and answer in lowercase only if it doesn't already exist
            existing_question = mongo.db.chats.find_one({"question": question_lowercase})
            if not existing_question:
                mongo.db.chats.insert_one({'question': question_lowercase, 'answer': f"{response['choices'][0]['text']}"})

        return jsonify(data)

    data = {"result": "Thank you! I'm just a machine learning model designed to respond to questions and generate text based on my training data. Is there anything specific you'd like to ask or discuss? "}

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
