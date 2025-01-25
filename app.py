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

from utils.logging import logger
from utils.ask_gemini import GeminiHelper

app = Flask(__name__)
gemini_helper = None

@app.route("/")
def hello() -> str:
    # Use basic logging with custom fields
    logger.info(logField="custom-entry", arbitraryField="custom-entry")

    # https://cloud.google.com/run/docs/logging#correlate-logs
    logger.info("Child logger with trace Id.")

    return "Hello, World!"

@app.route("/get_supplement", methods=["POST"])
def get_supplement() -> str:
    # Get JSON data from POST request
    chatdata_json = request.get_json()
    logger.info(f"Received data: {chatdata_json}")

    gemini_helper.add_text(chatdata_json["text"])
    jsondata_supplement = gemini_helper.ask_gemini()    

    return jsonify(jsondata_supplement)

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

    # Constructor
    gemini_helper = GeminiHelper()
else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
