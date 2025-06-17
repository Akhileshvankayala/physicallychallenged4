from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
from PIL import Image  # Importing from Pillow
import cv2  # OpenCV for capturing images
import time
import pyttsx3  # Text-to-Speech
import google.generativeai as genai
import speech_recognition as sr
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "akhileshvankayala158@gmail.com"  # Replace with your Gmail
SENDER_PASSWORD = "kqcouaozzjghilzr"  # Replace with your App Password without spaces
RECIPIENT_EMAIL = "thenighthorseanime@gmail.com"  # Replace with recipient's Gmail

# Configure logging
logging.basicConfig(level=logging.WARNING)

# Initialize Text-to-Speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # Adjust speaking speed

# Function to play voice prompts
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Predefined distances between locations in meters
DISTANCES = {
    'A Block': {'B Block': 80, 'C Block': 130, 'D Block': 170, 'E Block': 110, 'F Block': 80, 'G Block': 70, 'H Block': 220},
    'B Block': {'A Block': 80, 'C Block': 50, 'D Block': 100, 'E Block': 180, 'F Block': 160, 'G Block': 160, 'H Block': 140},
    'C Block': {'A Block': 130, 'B Block': 50, 'D Block': 110, 'E Block': 240, 'F Block': 210, 'G Block': 210, 'H Block': 150},
    'D Block': {'A Block': 170, 'B Block': 100, 'C Block': 110, 'E Block': 270, 'F Block': 250, 'G Block': 250, 'H Block': 40},
    'E Block': {'A Block': 110, 'B Block': 180, 'C Block': 240, 'D Block': 270, 'F Block': 20, 'G Block': 20, 'H Block': 300},
    'F Block': {'A Block': 80, 'B Block': 160, 'C Block': 210, 'D Block': 250, 'E Block': 20, 'G Block': 10, 'H Block': 290},
    'G Block': {'A Block': 70, 'B Block': 160, 'C Block': 210, 'D Block': 250, 'E Block': 20, 'F Block': 10, 'H Block': 290},
    'H Block': {'A Block': 220, 'B Block': 140, 'C Block': 150, 'D Block': 40, 'E Block': 300, 'F Block': 290, 'G Block': 290}
}

@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.json
    location = data.get("location")
    name = data.get("name")
    order = data.get("order")

    if not location or not order:
        return jsonify({"error": "Location and order details are required"}), 400

    # Create the order details table in HTML format
    order_table = """
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Name</th>
            <th>Price</th>
            <th>Quantity</th>
            <th>Subtotal</th>
        </tr>
    """
    total_amount = 0
    for item in order:
        subtotal = item['price'] * item['quantity']
        total_amount += subtotal
        order_table += f"""
        <tr>
            <td>{item['name']}</td>
            <td>{item['price']}</td>
            <td>{item['quantity']}</td>
            <td>{subtotal}</td>
        </tr>
        """
    order_table += f"""
        <tr>
            <td colspan="3" style="text-align:right"><strong>Total</strong></td>
            <td><strong>{total_amount}</strong></td>
        </tr>
    """
    order_table += "</table>"

    subject = "New Order Received"
    body = f"""
    <html>
    <body>
        <p>Location: {location}</p>
        <p>Name: {name}</p>
        <p>Order Details:</p>
        {order_table}
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()

        return jsonify({"message": "Order placed successfully and email sent!"}), 200
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/book_buggy', methods=['POST'])
def book_buggy():
    data = request.json
    name = data.get("name")
    pickup = data.get("pickup")
    dropoff = data.get("dropoff")

    if not name or not pickup or not dropoff:
        return jsonify({"error": "Name, pickup, and drop-off locations are required"}), 400

    # Calculate the distance between pickup and dropoff locations
    distance = DISTANCES.get(pickup, {}).get(dropoff, 0)

    # Create the booking details table in HTML format
    booking_table = f"""
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Pickup Location</th>
            <th>Drop-off Location</th>
            <th>Distance (meters)</th>
        </tr>
        <tr>
            <td>{pickup}</td>
            <td>{dropoff}</td>
            <td>{distance}</td>
        </tr>
    </table>
    """

    subject = "New Buggy Booking"
    body = f"""
    <html>
    <body>
        <p>Name: {name}</p>
        <p>New buggy booking details:</p>
        {booking_table}
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()

        return jsonify({"message": "Buggy booked successfully and email sent!"}), 200
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/submit_task', methods=['POST'])
def submit_task():
    data = request.json
    description = data.get("description")
    priority = data.get("priority")

    if not description or not priority:
        return jsonify({"error": "Task description and priority level are required"}), 400

    # Create the task details table in HTML format
    task_table = f"""
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Task Description</th>
            <th>Priority Level</th>
        </tr>
        <tr>
            <td>{description}</td>
            <td>{priority}</td>
        </tr>
    </table>
    """

    subject = "New Task Submission"
    body = f"""
    <html>
    <body>
        <p>New task submission details:</p>
        {task_table}
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()

        return jsonify({"message": "Task submitted successfully and email sent!"}), 200
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/request_service', methods=['POST'])
def request_service():
    data = request.json
    service_type = data.get("serviceType")
    location = data.get("location")
    duration = data.get("duration")

    if not service_type or not location or not duration:
        return jsonify({"error": "Service type, location, and duration are required"}), 400

    # Create the service request details table in HTML format
    service_table = f"""
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Service Type</th>
            <th>Location</th>
            <th>Duration (minutes)</th>
        </tr>
        <tr>
            <td>{service_type}</td>
            <td>{location}</td>
            <td>{duration}</td>
        </tr>
    </table>
    """

    subject = "New Mobility Service Request"
    body = f"""
    <html>
    <body>
        <p>New mobility service request details:</p>
        {service_table}
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()

        return jsonify({"message": "Service requested successfully and email sent!"}), 200
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return jsonify({"error": str(e)}), 500

# Set up Gemini API Key
api_key = os.getenv("VITE_API_KEY")
genai.configure(api_key=api_key)

# Function to get response from Gemini
def get_gemini_response(user_input):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  # Use a working model from Step 2
        response = model.generate_content(user_input)
        return response.text if response.text else "I couldn't generate a response."
    except Exception as e:
        return f"Error: {str(e)}\nCheck if you have access to this model in AI Studio."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    response_text = get_gemini_response(user_input)
    return jsonify({"response": response_text}), 200

# Capture image with live preview
def capture_image():
    cam = cv2.VideoCapture(0)  # Open the default camera (0)

    if not cam.isOpened():
        print("Error: Could not open camera.")
        return None

    speak("Opening camera. Get ready for the photo.")

    start_time = time.time()
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame.")
            break

        cv2.imshow("Live Camera - Auto Capture in 5s", frame)

        elapsed_time = time.time() - start_time
        if elapsed_time >= 5:  # Capture image after 5 seconds
            speak("Taking photo in 3... 2... 1...")
            image_path = "captured_image.jpg"
            cv2.imwrite(image_path, frame)  # Save image
            print("Image captured successfully!")
            break

        # Press 'q' to exit manually before auto-capture
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting without capturing.")
            image_path = None
            break

    cam.release()
    cv2.destroyAllWindows()
    return image_path

@app.route('/capture', methods=['POST'])
def capture():
    image_path = capture_image()

    if image_path:
        # Load the captured image
        sample_file = Image.open(image_path)

        # Choose a Gemini model
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

        # Create a prompt
        prompt = "Describe the image if there is a broken item or malfunctioned machine regarding physically handicapped and give suggestions or methods to fix the broken machine. If there are any medical-related tablets, tell about the symptoms and medication name."

        # Generate response
        response = model.generate_content([sample_file, prompt])

        # Display response
        if response and hasattr(response, "text"):
            return jsonify({"response": response.text, "imagePath": image_path}), 200
        else:
            return jsonify({"error": "No response received from Gemini API."}), 500
    else:
        return jsonify({"error": "No image captured."}), 500

@app.route('/speech', methods=['POST'])
def speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            return jsonify({"error": "No speech detected, try again."}), 400

    try:
        question = recognizer.recognize_google(audio)
        print(f"You said: {question}")
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand the audio"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Speech Recognition Error: {e}"}), 500

    response_text = get_gemini_response(question)
    return jsonify({"question": question, "response": response_text}), 200

if __name__ == '__main__':
    app.run(debug=True)