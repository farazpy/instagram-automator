from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import logging
from instagrapi import Client
from instagrapi.exceptions import BadPassword, ChallengeRequired, LoginRequired, ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='instagram_session.log'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Constants
SESSION_FOLDER = "session"
COMMON_PASSWORD = ""  # Set your common password here
ACCOUNTS_FILE = "accounts.json"

class InstagramSessionManager:
    def __init__(self, password: str):
        self.password = password
        os.makedirs(SESSION_FOLDER, exist_ok=True)
        
        self.device_settings = {
            "cpu": "Exynos 2400",
            "dpi": "500dpi",
            "model": "SM-S926B",
            "device": "Samsung Galaxy S24 Ultra",
            "resolution": "3088x1440",
            "app_version": "300.0.0.28.109",
            "manufacturer": "Samsung",
            "version_code": "300001010",
            "android_release": "14.0",
            "android_version": 34
        }
        
        self.user_agent = (
            "Instagram 300.0.0.28.109 iOS (18.0; iPhone15,3; 460dpi; "
            "2796x1290; Apple; iPhone 15 Pro Max; en_US)"
        )

    def create_session(self, username: str) -> dict:
        try:
            session_file = os.path.join(SESSION_FOLDER, f"{username}.json")
            cl = Client()
            
            if os.path.exists(session_file):
                cl.load_settings(session_file)
                logger.info(f"Session loaded from file for {username}")
                return {"success": True, "message": "Session already exists"}
            
            cl.set_device(self.device_settings)
            cl.set_country("IN")
            cl.set_country_code(91)
            cl.set_user_agent(self.user_agent)
            
            cl.login(username, self.password)
            cl.dump_settings(session_file)
            logger.info(f"Logged in and session saved for {username}")
            return {"success": True, "message": "Login successful"}
            
        except (BadPassword, ChallengeRequired, LoginRequired, ClientError) as e:
            logger.error(f"Login failed for {username}: {str(e)}")
            return {"success": False, "message": f"Login failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error for {username}: {str(e)}")
            return {"success": False, "message": f"Unexpected error: {str(e)}"}

def load_accounts():
    try:
        with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, indent=2)

@app.route('/')
def index():
    accounts = load_accounts()
    usernames = [account['username'] for account in accounts]
    return render_template('index.html', usernames=usernames)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if not username:
        return jsonify({"success": False, "message": "No username selected"})
    
    session_manager = InstagramSessionManager(COMMON_PASSWORD)
    result = session_manager.create_session(username)
    
    if result["success"]:
        # Remove successful login from accounts.json
        accounts = load_accounts()
        accounts = [acc for acc in accounts if acc['username'] != username]
        save_accounts(accounts)
    
    return jsonify(result)

# HTML template
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Instagram Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        select, button {
            padding: 8px;
            width: 100%;
            margin-top: 5px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>Instagram Login</h1>
    <div class="form-group">
        <label for="username">Select Username:</label>
        <select id="username" name="username">
            {% if usernames %}
                {% for username in usernames %}
                    <option value="{{ username }}">{{ username }}</option>
                {% endfor %}
            {% else %}
                <option value="">No accounts available</option>
            {% endif %}
        </select>
    </div>
    <button onclick="login()">Login</button>

    <script>
        function login() {
            const username = document.getElementById('username').value;
            if (!username) {
                alert('Please select a username');
                return;
            }

            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'username=' + encodeURIComponent(username)
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                if (data.success) {
                    location.reload();
                }
            })
            .catch(error => {
                alert('Error: ' + error.message);
            });
        }
    </script>
</body>
</html>
"""

# Create templates directory and save the HTML
if not os.path.exists('templates'):
    os.makedirs('templates')
with open('templates/index.html', 'w') as f:
    f.write(html_template)

if __name__ == '__main__':
    app.run(debug=True)