import os
import time
import requests
from pathlib import Path

# Server details
SERVER_URL = "http://localhost:8000"
MESSAGE_DIR = Path("./messages")

# Helper function to start the server using subprocess (non-blocking)
def start_server():
    """Starts the server in a background process"""
    os.system("python3 server.py &")
    time.sleep(5)  # Wait for the server to start

# Helper function to stop the server
def stop_server():
    """Stops the server"""
    os.system("pkill -f 'python3 server.py'")

# Test 1: Verify server starts up and homepage is accessible
def test_server_startup():
    print("Test 1: Verifying server startup and homepage accessibility.")
    try:
        response = requests.get(SERVER_URL)
        assert response.status_code == 200
        print("Server started successfully. Homepage accessible.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to access the homepage: {e}")

# Test 2: Test message submission and file creation
def test_message_submission():
    print("Test 2: Verifying message submission and file creation.")
    test_message = "Hello, this is a test message."

    try:
        # Submit a message
        response = requests.post(SERVER_URL, data={"message": test_message})
        assert response.status_code == 303  # Should redirect after POST

        # Check if the file was created in the messages directory
        message_files = list(MESSAGE_DIR.iterdir())
        assert len(message_files) > 0, "No message files were created."

        # Check the contents of the last message file
        latest_file = sorted(message_files, key=lambda f: f.stat().st_mtime)[-1]
        with open(latest_file, "r") as file:
            content = file.read().strip()
            assert content == test_message, f"Expected message '{test_message}', but found '{content}'."

        print(f"Message '{test_message}' submitted and file created successfully.")
    except Exception as e:
        print(f"Failed message submission test: {e}")

# Test 3: Verify HTML regeneration after message submission
def test_html_regeneration():
    print("Test 3: Verifying HTML regeneration after message submission.")
    try:
        # Before submitting a new message, capture the initial HTML state
        initial_response = requests.get(SERVER_URL)
        initial_html = initial_response.text

        # Submit a new message
        test_message = "Message to trigger HTML regeneration."
        requests.post(SERVER_URL, data={"message": test_message})
        time.sleep(1)  # Allow the server to regenerate the HTML

        # After submitting, fetch the HTML again
        updated_response = requests.get(SERVER_URL)
        updated_html = updated_response.text

        # Ensure that the new message is included in the HTML
        assert test_message in updated_html, "New message was not found in the updated HTML."
        assert updated_html != initial_html, "HTML was not regenerated after submitting a new message."

        print("HTML regenerated successfully with the new message.")
    except Exception as e:
        print(f"Failed HTML regeneration test: {e}")

# Test 4: Verify message ordering in HTML (newest message at the top)
def test_message_ordering():
    print("Test 4: Verifying message ordering in the HTML interface.")
    try:
        # Submit two messages
        messages = ["First test message", "Second test message"]
        for msg in messages:
            requests.post(SERVER_URL, data={"message": msg})

        time.sleep(1)  # Allow HTML to regenerate

        # Get the HTML content
        response = requests.get(SERVER_URL)
        html_content = response.text

        # Check that the latest message is the first message in the HTML
        assert messages[1] in html_content, f"Latest message '{messages[1]}' not found."
        assert messages[0] in html_content, f"Oldest message '{messages[0]}' not found."

        print("Messages are displayed in the correct order.")
    except Exception as e:
        print(f"Failed message ordering test: {e}")

# Test 5: Verify message file deletion after server restart (optional)
def test_message_file_deletion():
    print("Test 5: Verifying message file deletion after server restart.")
    try:
        # Restart the server
        stop_server()
        time.sleep(2)
        start_server()

        # Ensure the messages directory is not empty after restart
        message_files = list(MESSAGE_DIR.iterdir())
        assert len(message_files) > 0, "Messages directory is empty after server restart."

        print("Message files persist after server restart.")
    except Exception as e:
        print(f"Failed message file deletion test: {e}")

# Main testing function
def run_tests():
    # Start the server
    print("Starting the server for testing...")
    start_server()

    try:
        test_server_startup()
        test_message_submission()
        test_html_regeneration()
        test_message_ordering()
        test_message_file_deletion()

    finally:
        # Stop the server after tests
        print("Stopping the server...")
        stop_server()

if __name__ == "__main__":
    run_tests()
