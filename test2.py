from flask import Flask, render_template, request
import streamlit as st
from ctransformers import AutoModelForCausalLM

app = Flask(__name__)

# Load the model
llm = AutoModelForCausalLM.from_pretrained(
    model_path_or_repo_id="mistral-7b-instruct-v0.1.Q2_K.gguf",
    model_type="mistral",
)

@app.route('/')
def home():
    return render_template('test1.html')

# Function to generate response
def generate_response(user_query):
    prompt = f"""The user query is {user_query} """
    args = {
        "prompt": prompt,
        "stream": True,
        "max_new_tokens": 4096,
        "temperature": 0,
    }
    response_so_far = ""  # Initialize empty string to store cumulative response
    for chunk in llm(**args):
        response_so_far += chunk  # Append current chunk to cumulative response
    return response_so_far

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_query = request.form['user_query']
        response = generate_response(user_query)
        return render_template('chat.html', user_query=user_query, response=response)
    else:
        return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)
