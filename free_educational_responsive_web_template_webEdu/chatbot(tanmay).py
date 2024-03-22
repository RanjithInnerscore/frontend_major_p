import os
import json
import numpy as np
import sys
import glob

import requests

os.environ["OPENAI_API_KEY"] = "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"
os.environ["HUGGINGFACE_API_TOKEN"] = "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"
HUGGINGFACE_API_TOKEN = "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"

import openai
import time
from flask import request
from flask import Flask, Response
from flask_cors import CORS, cross_origin


def get_subtl_auth():
    username = "ram.chinta@innerscore.com"
    password = "Subtl@2023"

    auth_url = "https://app.subtl.ai/api/auth/login"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }

    response = requests.post(auth_url, headers=headers, data=data)
    response = response.json()
    try:
        auth_token = response["access_token"]

        print("Authentication Successful")
        print("Auth token: ", auth_token)
        return auth_token
    except:
        print("Authentication Unsucessful")
        print("Response: ", response)
        return (-1)


def subtl_transaction(auth_token, combined_query, chapter_id, k):
    url = 'https://app.subtl.ai/api/transactions'
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    data = {
        "query_string": combined_query,
        "target_id": chapter_id,
        "internal_query": False
    }
    print("Combined Query: ", combined_query)
    print("Chapter_id: ", chapter_id)

    response = requests.post(url, headers=headers, json=data)
    response = response.json()

    subtl_chunks = []
    for i in range(len(response["answers"])):
        subtl_chunks.append(response["answers"][i]["answer"])

    k_subtl_chunks = subtl_chunks[:k]  # Get top k chunks
    return k_subtl_chunks


def get_sublt_chunks(query, chat_history, topic, subject, grade, k):
    combined_query = ""
    for i in range(len(chat_history)):
        if (chat_history[i]["role"] == "user"):
            prev_query = chat_history[i]["content"].replace("Query: ", "")
            combined_query = combined_query + prev_query + " "
    combined_query = combined_query + query

    chapter_id = ""
    group_name = "class_%s-%s" % (grade, subject)
    for chapter in collection.find():
        if (chapter["chapter_name"] == topic and chapter["group_name"] == group_name):
            chapter_id = chapter["chapter_id"]

    auth_token = get_subtl_auth()
    subtl_chunks_array = subtl_transaction(auth_token, combined_query, chapter_id, k)
    print("**********CHUNKS**********")
    for i in range(len(subtl_chunks_array)):
        print(subtl_chunks_array[i])

    return subtl_chunks_array


def prepare_roles_inContext(chat_history, prompt, subtl_chunks):
    subtl_chunks_flatten = ""
    for i in range(len(subtl_chunks)):
        subtl_chunks_flatten = subtl_chunks_flatten + subtl_chunks[i] + "\n"

    messages_created_array = [{"role": "system", "content": "%s\n------%s" % (prompt, subtl_chunks_flatten)}]
    for i in range(len(chat_history)):
        # Make a single entry for chat_history with role - chat history
        messages_created_array.append(chat_history[i])

    return messages_created_array


def prepare_roles_bypass(chat_history, prompt):
    messages_created_array = [{"role": "system", "content": "%s" % (prompt)}]
    for i in range(len(chat_history)):
        # Make a single entry for chat_history with role - chat history
        messages_created_array.append(chat_history[i])
    return messages_created_array


def generate_response_llm(message_array, model):
    print(message_array)
    completion = openai.ChatCompletion.create(
        model=model,
        messages=message_array,
        stream=True)

    bulk_response = ""
    for stream_chunks in completion:
        try:
            sys.stdout.write(
                stream_chunks["choices"][0]["delta"]["content"] + '')  # Use sys.stdout.write instead of print
            sys.stdout.flush()  # Flush the buffer to ensure real-time printing)

            chunk_words = stream_chunks["choices"][0]["delta"]["content"]
            chunk_words = repr(chunk_words)
            strip_chunk_words = chunk_words.strip("'")
            yield f"data:{strip_chunk_words}\n\n"

            bulk_response = bulk_response + stream_chunks["choices"][0]["delta"]["content"]
        except:
            continue

    # chat_response = completion["choices"][0]["message"]["content"]
    print("\nBulk Response: ", repr(bulk_response))
    return bulk_response


##############

def engmundu(grade, lesson, query, chat_history):
    directory = "engtext"
    lesson_path = os.path.join(directory, str(grade), lesson + '.txt')

    if not os.path.exists(lesson_path):
        print(f"Lesson {lesson} in grade {grade} does not exist.")
        return
    with open(lesson_path, "r") as file:
        lesson_content = file.read()
    prompt = "Answer the English question from the lesson: " + lesson_content
    return(prompt)

##############

def prepare_prompt(grade, subject, topic, learning_method, interaction):
    grade = grade.replace(" ", "_").lower().strip()
    subject = subject.replace(" ", "_").lower().strip()
    topic = topic.replace(" ", "_").lower().strip()

    prompt_collection = db["ai-assist-prompts"]
    query = {
        "grade": grade,
        "subject": subject,
        "topic": topic,
        "learning_method": learning_method,
        "interaction": interaction
    }

    prompt = ""
    try:
        result = prompt_collection.find_one(query)
        print(result)
        prompt = result.get("prompt")
    except:
        prompt = "Prompt not found"
        print("************%s********" % (prompt))
    return prompt


app = Flask(__name__)
CORS(app)


@app.route('/ai-assist-stream', methods=['POST'])
def chatbot_stream_subtl():
    api_body = request.get_json()
    query = api_body["query"]
    chat_history = api_body["chat_history"]

    # prompt = api_body["prompt"]#can't come from front-end
    k = 3  # Default value. Using esacpe as math has no k value.
    try:
        k = api_body["k"]  # no of text chunks
    except:
        pass
    model = api_body["model"]

    grade = str(api_body["grade"]).lower()
    subject = str(api_body["subject"]).lower()
    subject = subject.replace(" ", "_")
    topic = str(api_body["topic_name"]).lower()
    topic = topic.replace(" ", "_")

    print("Topic: ", topic)

    interaction = api_body["interaction"].lower()  # Regular or Socratic

    learning_method = "in-context"  # Default
    if (subject == "math" or (subject == "english" and topic == "grammar")):
        learning_method = "bypass"

    ##################

    if subject == "english" and topic != "grammar":
        print("hi")
        engmundu(grade,topic,query, chat_history)
        learning_method= "literature"

    ##################

    if (subject == "science" or subject == "physics" or subject == "chemistry"):
        # Classifier response changes the learning_method
        learning_method = "bypass"  # Default till classifier is up!
        pass

    message_array = []
    if (learning_method == "in-context"):
        # To choose chunks, we will have to combine previous queries.
        prompt = prepare_prompt(grade, subject, topic, learning_method, interaction)
        subtl_chunks = get_sublt_chunks(query, chat_history, topic, subject, grade, k)
        message_array = prepare_roles_inContext(chat_history, prompt, subtl_chunks)  # message array to GPT
    if (learning_method == "bypass"):
        prompt = prepare_prompt(grade, subject, topic, learning_method, interaction)
        message_array = prepare_roles_bypass(chat_history, prompt)  # message array to GPT
    #################################
    if (learning_method == "literature"):
        prompt1 = engmundu(grade, topic, query, chat_history)
        message_array = prepare_roles_bypass(chat_history, prompt1)
        message_array.append({"role": "user", "content": "Query: %s" % (query)})  # Add the newest query to the message_array

        #################################
    return Response(generate_response_llm(message_array, model), mimetype='text/event-stream')


if __name__ == "__main__":
    # app.run(host="0.0.0.0") #Uncomment while deploying
    app.run(port=5001, debug=True)