from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import logging
import traceback
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS
CORS(app)

# Configuration variables - replace these with your actual values
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = os.environ.get("LANGFLOW_ID", "9a651376-1593-4fec-ae77-58a912a5032e")
FLOW_ID = os.environ.get("FLOW_ID", "01330d3c-d0e2-439c-a69f-8c6071ed99cf")
APPLICATION_TOKEN = os.environ.get("APPLICATION_TOKEN")

def validate_token():
    """Validate that the token is properly configured."""
    if not APPLICATION_TOKEN or APPLICATION_TOKEN.strip() == "":
        logger.error("Token is empty or not set")
        return False
    return True

def run_flow(message, endpoint, output_type="chat", input_type="chat", application_token=None):
    """Run a flow with a given message."""
    try:
        api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
        payload = {
            "input_value": message,
            "output_type": output_type,
            "input_type": input_type,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {application_token}"
        }
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error in run_flow: {e}")
        logger.error(traceback.format_exc())
        raise

@app.route('/')
def serve_html():
    """Serve the main HTML page."""
    return app.send_static_file('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests."""
    try:
        data = request.json
        logger.info(f"Received chat request: {data}")
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400

        message = data.get('message')
        endpoint = data.get('endpoint', FLOW_ID)
        output_type = data.get('output_type', 'chat')
        input_type = data.get('input_type', 'chat')

        response = run_flow(
            message=message,
            endpoint=endpoint,
            output_type=output_type,
            input_type=input_type,
            application_token=APPLICATION_TOKEN
        )
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    if validate_token():
        logger.info("Token validation successful, starting server...")
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    else:
        logger.error("Server not started due to token configuration issue")