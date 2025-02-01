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
from utils.meeting_summarizer import MeetingSummarizer
import utils.ask_gemini as ask_gemini
import utils.connect_firestore as connect_firestore

app = Flask(__name__)
# gemini_helper = dict()
meeting_summarizer = MeetingSummarizer()

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


@app.route("/summarize_meeting", methods=["GET"])
def summarize_meeting() -> str:
    try:
        # サンプルミーティングファイルを読み込む
        with open("utils/sample_meeting.txt", "r", encoding="utf-8") as file:
            meeting_text = file.read()

        # 会議内容を要約
        summary = meeting_summarizer.summarize(meeting_text)

        return jsonify({"status": "success", "data": summary})
    except Exception as e:
        logger.error(f"Error summarizing meeting: {str(e)}")
        return jsonify({"status": "error", "message": "会議の要約中にエラーが発生しました"}), 500

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
    save_transcript: Save transcript data to Firestore
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
            # Save the transcript data to Firestore
            transcript_text = ""
            
            # Get the transcript data from Firestore
            firestore_data = connect_firestore.get_data("meeting", chatdata_json["meetId"])
            
            # If the transcript data exists, add the new transcript text to the existing transcript text
            if firestore_data:
                transcript_text = firestore_data["transcript"] + chatdata_json["transcript"]
            # If the transcript data does not exist, save the new transcript text
            else:
                transcript_text = chatdata_json["transcript"] 

            # Save the transcript data to Firestore
            connect_firestore.update_data("meeting", chatdata_json["meetId"], {"transcript": transcript_text})
            
            # Log the saved transcript
            logger.info(f"Transcript saved: {transcript_text}")
            jsondata_save = {
                "result": True,
                "message": ""
            }
        else:
            # If the json data does not have the required keys, return error message
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
    :param: meetId: str
    :param: userName: str
    :param: role: str
    :return: response: dict
    """
    # Get JSON data from POST request
    chatdata_json = request.get_json()
    logger.info(f"Received data: {chatdata_json}")

    # Store the supplement data and return it
    supplements_data = list(dict())

    try:
        # Check if the json data has the required keys
        if ("meetId" in chatdata_json and "userName" in chatdata_json and "role" in chatdata_json):
            # Get the transcript data from Firestore
            transcript_data = connect_firestore.get_data("meeting", chatdata_json["meetId"])
            if transcript_data:
                # Get the transcript text from the transcript data
                transcript_text = transcript_data["transcript"]
                # Get the supplement data from the Gemini API
                supplements = ask_gemini.word_extraction(chatdata_json["role"], transcript_text)
                
                # Get the document list from Firestore
                saved_words = connect_firestore.get_word_list("users", chatdata_json["userName"])
                
                # Match the document list with the word list
                for supplement in supplements:
                    if supplement["word"] not in saved_words:
                        # Add the supplement data to the supplement list
                        supplements_data.append(supplement)
                        # Add the supplement data to Firestore
                        connect_firestore.add_data("users", chatdata_json["userName"], supplement)
                    else:
                        pass
            # If the transcript data does not exist, return empty supplement data
            else:
                supplements_data = []


            jsondata_supplement = {
                "supplement": supplements_data,
                "result": True,
                "message": ""
            }
        else:
            # If the json data does not have the required keys, return error message
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
        # Check if the json data has the required keys
        if ("meetId" in chatdata_json):
            jsondata_end = {
                "result": True,
                "message": ""
            }
        else:
            # If the json data does not have the required keys, return error message
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
