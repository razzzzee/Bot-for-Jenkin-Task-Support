from flask import Flask, Response
from flask import request, jsonify, make_response
import json
import logging
from flask_cors import CORS
from bot_api import bot_actions
from config.config_reader import ConfigReader

app = Flask(__name__)
CORS(app)
logging.basicConfig(filename='../app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
jenkins_config = None


@app.route('/bot_webhook', methods=['POST'])
def handle_bot_action():
    request_json_data = request.get_json(silent=True, force=True)
    logging.debug(json.dumps(request_json_data))
    request_action = request_json_data['queryResult']['action']
    response_text = invoke_bot_action(request_json_data, request_action)
    return generate_response(response_text)


def invoke_bot_action(request_json_data, request_action):
    bot_action_executor= bot_actions.BotActions()
    if request_action == "build_promotion":
        logging.info('promoting build')
        response_text = bot_action_executor.promote_build(request_json_data)

    elif request_action == "abort_job_by_name":
        logging.info('aborting job by name')
        response_text = bot_action_executor.abort_job_by_name(request_json_data)

    elif request_action == "retrieve_build_status_by_job_name" or request_action == "retrieve_pass_fail_count":
        logging.info("retrieve build status by job name/ pass fail count")
        response_text = bot_action_executor.retrieve_job_status(request_json_data)

    # elif request_action == "retrieve_build_status_by_job_type":
    #     logging.info("retrieve_build_status_by_job_type")
    #     response_text = bot_action_executor.retrieve_job_status_by_type(request_json_data)

    elif request_action == "retrieve_changeset_details":
        logging.info("retrieve changeset details")
        response_text = bot_action_executor.retrieve_changeset_details(request_json_data)

    # elif request_action == "retrieve_pass_fail_count":
    #     logging.info("retrieving pass failure count")
    #     response_text = bot_action_executor.retrieve_pass_fail_count(request_json_data)

    elif request_action == "invoke_test_suite":
        logging.info("invoking test suite")
        response_text = bot_action_executor.invoke_test_suite(request_json_data)

    elif request_action == "retry_job":
        logging.info("retrying to run job")
        response_text = bot_action_executor.rerun_job(request_json_data)

    elif request_action == "trigger_build":
        logging.info("triggering build")
        response_text = bot_action_executor.trigger_build(request_json_data)
    else:
        response_text = "didnt understood your statement"
        print(request_action)
    return response_text


# generates response from given response text
def generate_response(response_text):
    logging.info(response_text)
    return Response(json.dumps({'fulfillmentText': response_text}), status=200, mimetype='application/json')


# return Response(json.dumps(response_data), status=200, mimetype='application/json')
if __name__ == "__main__":
    app.run(port=4200, debug=True)


 # format of response for v2 api
    # response_data = {
    #     "fulfillmentText": response_text,
    #     "fulfillmentMessages": [
    #         {
    #             "text": response_text
    #         }
    #     ],
    #     "source": "bot backend",
    #     "payload": {},
    #     "outputContexts": [],
    #     "followupEventInput": {}
    # }