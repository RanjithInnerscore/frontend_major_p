from flask import Flask, render_template, request
import requests
import json
from flask import Flask, request, render_template, session, redirect, url_for
import requests


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/price.html', methods=['GET', 'POST'])
def price():
    if request.method == 'POST':
        # Get the selected topic from the form
        selected_topic = request.form['userInput']
        
        # API URL for question bank generator
        URL = "https://005d-34-74-93-4.ngrok-free.app/coteacher/qbGenerator"
        
        # Example JSON payload
        payload = {"topic_id": selected_topic}

        # Set the Content-Type header to indicate JSON data
        headers = {"Content-Type": "application/json"}
        
        # Make the POST request with the payload and headers
        response = requests.post(URL, json=payload, headers=headers)

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            try:
                # Try to parse the JSON response
                response_content = response.json()
            except json.JSONDecodeError:
                # If JSON decoding fails, handle the error
                return "Error: Unable to decode JSON response from the server"
            
            # Extract the questions from the response
            questions = response_content
            print(questions)
            URL = "https://005d-34-74-93-4.ngrok-free.app/coteacher/compute_duplicates"
            if request.method == 'POST':
            # Render the questions template with the extracted questions
            return render_template('questions.html', questions=questions)
        else:
            return f"Error: Server returned status code {response.status_code}"

    # If it's a GET request, render the price.html template
    return render_template('price.html')

@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get the selected topic from the form
        selected_topic = request.json.get('userInput')
        selected_topic_number = request.json.get('userInput1')

        print(selected_topic)
        print(selected_topic_number)
        
        # API URL for script generator
        URL = "https://5f14-34-86-212-56.ngrok-free.app/coteacher/scriptgenerator"
        
        # Example payload
        payload = {"topic": selected_topic, "number": selected_topic_number}

        # Set the Content-Type header to indicate JSON data
        headers = {"Content-Type": "application/json"}

        # Make the POST request with the payload and headers
        response = requests.post(URL, json=payload, headers=headers)

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            # Return the response content directly
            return response.text
        else:
            return f"Error: Server returned status code {response.status_code}"
    
    # If it's a GET request, render the contact.html template
    return render_template('contact.html')


@app.route('/videos.html', methods=['GET', 'POST'])
def videos():
    if request.method == 'POST':
        # Get the selected topic from the form
        selected_topic = request.form.get('userInput')

        print(selected_topic)
        
        URL = "https://17f5-35-204-89-105.ngrok-free.app/coteacher/scriptgenerator"
        
        # Example payload
        payload = {"topic_id": selected_topic}

        print(payload)

        # Set the Content-Type header to indicate text/plain data
        headers = {"Content-Type": "application/json"}

        # Make the POST request with the payload and headers
        response = requests.post(URL, data=json.dumps(payload), headers=headers)
        print(response)

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            # Return the response content directly
            return response.text
        else:
            return f"Error: Server returned status code {response.status_code}"
    
    # If it's a GET request, render the contact.html template
    return render_template('videos.html')


@app.route('/courses.html', methods=['GET', 'POST'])
def courses():
    if request.is_json:
        data = request.get_json()
        print(data)
    else:
        print('Not JSON')
        selected_topic = request.form.get('userInput')
        selected_topic = json.loads(selected_topic)
        print(selected_topic)
    if request.method == 'POST':

        selected_topic = request.json.get('userInput')

        print(selected_topic)
        
        # API URL for script generator
        URL = "https://5f14-34-86-212-56.ngrok-free.app/coteacher/chat"
        
        print(URL)
        # Example payload
        payload = {"topic": selected_topic}

        # Set the Content-Type header to indicate text/plain data
        headers = {"Content-Type": "application/json"}

        # Make the POST request with the payload and headers
        response = requests.post(URL, data=json.dumps(payload), headers=headers)

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            # Return the response content directly
            return response.text
        else:
            return f"Error: Server returned status code {response.status_code}"
    
    # If it's a GET request, render the contact.html template
    return render_template('courses.html')


if __name__ == '__main__':
    app.run(debug=True,host = "0.0.0.0",port = 5001)
