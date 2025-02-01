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

@app.route("/start_meet", methods=["POST"])
def start_meet() -> str:
    """
    start_meet: Start a new meet with a new userName
    :param: meetId: str
    :return: response: dict
    """
    # Get JSON data from POST request
    chatdata_json = request.get_json()
    logger.info(f"Received data: {chatdata_json}")

    # Start a new meet with a new meetId
    try:
        if ("meetId" in chatdata_json):
            # Return the meetId as the userName
            jsondata_start = {
                "result": True,
                "message": ""
            }
        else:
            jsondata_start = {
                "result": False,
                "message": "missing required keys"
            }
    except Exception as e:
        logger.error(f"Error starting meet: {e}")
        jsondata_start = {
            "result": False,
            "message": "error starting meet"
        }

    response = jsonify(jsondata_start)
    return response

@app.route("/save_transcript", methods=["POST"])
def save_transcript() -> str:
    """
    save_transcript: Save transcript data to gemini_helper
    :param: meetId: str
    :param: userName: str
    :param: transcript: str
    :return: response: dict
    """
    # Get JSON data from POST request
    chatdata_json = request.get_json()
    logger.info(f"Received data: {chatdata_json}")

    # Store the text date to the Firestrore
    try:
        # Check if the json data has the required keys
        if ("meetId" in chatdata_json and "userName" in chatdata_json and "transcript" in chatdata_json):
            jsondata_save = {
                "result": True,
                "message": ""
            }
        else:
            jsondata_save = {
                "result": False,
                "message": "missing required keys"
            }
    except Exception as e:
        logger.error(f"Error saving transcript: {e}")
        jsondata_save = {
            "result": False,
            "message": "error saving transcript"
        }

    response = jsonify(jsondata_save)
    return response


@app.route("/get_supplement", methods=["POST"])
def get_supplement() -> str:
    """
    get_supplement: Get supplement data from Gemini API
    :param: userName: str
    :param: text: str
    :return: response: dict
    """
    # Get JSON data from POST request
    chatdata_json = request.get_json()
    logger.info(f"Received data: {chatdata_json}")

    try:
        # Check if userName exists in gemini_helper
        if ("meetId" in chatdata_json and "userName" in chatdata_json and "role" in chatdata_json):
            testdata = {
                "word": "テスト文章",
                "description": "テスト補足"
            }
            jsondata_supplement = {
                "supplement": [testdata],
                "result": True,
                "message": ""
            }
        else:
            # If userName does not exist, return error message
            jsondata_supplement = {
                "supplement": [],
                "result": False,
                "message": "missing required keys"
            }
    except Exception as e:
        logger.error(f"Error getting supplement: {e}")
        jsondata_supplement = {
            "supplement": [],
            "result": False,
            "message": "error getting supplement"
        }

    response = jsonify(jsondata_supplement)
    return response

@app.route("/end_meet", methods=["POST"])
def end_meet() -> str:
    """
    end_meet: End meet with meetId
    :param: meetId: str
    :return: response: dict
    """
    # Get JSON data from POST request
    chatdata_json = request.get_json()
    logger.info(f"Received data: {chatdata_json}")

    try:
        # Check if userName exists in gemini_helper
        if ("meetId" in chatdata_json):
            jsondata_end = {
                "result": True,
                "message": ""
            }
        else:
            # If userName does not exist, return error message
            jsondata_end = {
                "result": False,
                "message": "missing required keys"
            }
    except Exception as e:
        logger.error(f"Error ending meet: {e}")
        jsondata_end = {
            "result": False,
            "message": "error ending meet"
        }

    response = jsonify(jsondata_end)
    return response

def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    from utils.logging import flush
from google.cloud import firestore

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
