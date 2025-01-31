# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import signal
import sys
from types import FrameType

from flask import Flask, jsonify, request
from flask_cors import CORS

from utils.logging import logger
from utils.ask_gemini import GeminiHelper

app = Flask(__name__)
gemini_helper = dict()

CORS(
    app,
    resources={
        r"/*": {
            "origins": ["*", "chrome-extension://*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    },
)


@app.route("/")
def hello() -> str:
    # Use basic logging with custom fields
    logger.info(logField="custom-entry", arbitraryField="custom-entry")

    # https://cloud.google.com/run/docs/logging#correlate-logs
    logger.info("Child logger with trace Id.")

    return "Hello, World!"

@app.route("/start_conversation", methods=["POST"])
def start_conversation() -> str:
    """
    start_conversation: Start a new conversation with a new session_id
    :param: session_id: str
    :return: response: dict
    """
    # Get JSON data from POST request
    chatdata_json = request.get_json()
    logger.info(f"Received data: {chatdata_json}")

    try:
        # Check if session_id exists in gemini_helper
        if (not gemini_helper.keys(chatdata_json["session_id"])):
            gemini_helper[chatdata_json["session_id"]] = GeminiHelper()
            jsondata_start = {
                "result": True,
                "message": "Conversation started"
            }
        else:
            # If session_id exists, return error message
            jsondata_start = {
                "result": False,
                "message": "session_id already exists"
            }
    except KeyError:
        # If session_id does not exist, return error message
        jsondata_start = {
            "result": False,
            "message": "keyError"
        }

    response = jsonify(jsondata_start)
    return response

@app.route("/get_supplement", methods=["POST"])
def get_supplement() -> str:
    """
    get_supplement: Get supplement data from Gemini API
    :param: session_id: str
    :param: text: str
    :return: response: dict
    """
    # Get JSON data from POST request
    chatdata_json = request.get_json()
    logger.info(f"Received data: {chatdata_json}")

    try:
        # Check if session_id exists in gemini_helper
        if (not gemini_helper.keys(chatdata_json["session_id"])):        
            # If session_id exists, add text to gemini_helper and ask gemini
            gemini_helper[chatdata_json["session_id"]].add_text(chatdata_json["text"])
            jsondata_supplement = gemini_helper[chatdata_json["session_id"]].ask_gemini()
            jsondata_supplement["result"] = True  
        else:
            # If session_id does not exist, return error message
            jsondata_supplement = {
                "supplement": [],
                "result": False,
                "message": "No session_id found"
            }
    except KeyError:
        # If session_id does not exist, return error message
        jsondata_supplement = {
            "supplement": [],
            "result": False,
            "message": "keyError"
        }

    response = jsonify(jsondata_supplement)
    return response

@app.route("/end_conversation", methods=["POST"])
def end_conversation() -> str:
    """
    end_conversation: End conversation with session_id
    :param: session_id: str
    :return: response: dict
    """
    # Get JSON data from POST request
    chatdata_json = request.get_json()
    logger.info(f"Received data: {chatdata_json}")

    try:
        # Check if session_id exists in gemini_helper
        if (not gemini_helper.keys(chatdata_json["session_id"])):        
            # If session_id exists, end conversation
            gemini_helper.pop(chatdata_json["session_id"])
            jsondata_end = {
                "message": "Conversation ended",
                "result": True
            }
        else:
            # If session_id does not exist, return error message
            jsondata_end = {
                "message": "No session_id found",
                "result": False
            }
    except KeyError:
        # If session_id does not exist, return error message
        jsondata_end = {
            "message": "keyError",
            "result": False
        }

    response = jsonify(jsondata_end)
    return response

def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    from utils.logging import flush

    flush()

    # Safely exit program
    sys.exit(0)


if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment

    # handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=True)

else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
