from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/price.html', methods=['GET', 'POST'])
def price():
    if request.method == 'POST':
        # Get the selected topic from the form
        selected_topic = request.form['userInput']
        
        # API URL
        URL = "https://8eb2-35-231-58-214.ngrok-free.app/coteacher/qbGenerator"
        
        # Example JSON payload
        payload = {"topic_id": selected_topic}

        # Set the Content-Type header to indicate JSON data
        headers = {"Content-Type": "application/json"}
        print ("sent")
        # Make the POST request with the payload and headers
        response = requests.post(URL, json=payload, headers=headers)

        # Get the JSON response content
        response_content = response.json()
        
        # Extract the questions from the response
        questions = response_content
        
        # Render the questions template with the extracted questions
        return render_template('questions.html', questions=questions)
    
    # If it's a GET request, render the price.html template without any response
    return render_template('price.html')

@app.route('/contact.html', methods=['GET', 'POST'])

def contact():
    if request.method == 'POST':
        selected_topic = request.form.get('userInput')
        URL = "https://8eb2-35-231-58-214.ngrok-free.app/coteacher/scriptgenerator"
        payload = {"topic_id": selected_topic}
        headers = {"Content-Type": "application/json"}

        response = requests.post(URL, json=payload, headers=headers)

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            return "Error: Unable to decode JSON response from the server"
        
        return response_data
    
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
