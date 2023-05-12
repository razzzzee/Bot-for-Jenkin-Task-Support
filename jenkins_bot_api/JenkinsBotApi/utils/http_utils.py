"""
@description: requests services for GET,POST
@author: Sukan Singh
"""

import requests
import logging

logging.basicConfig(filename='../app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
# username = "sukansingh"
# password = "Sukan@123"


class HttpUtils:
    def __init__(self, jenkins_config):
        self.username = jenkins_config['host_config']['username']
        self.password = jenkins_config['host_config']['password']

    def execute_get_service(self, url):
        # print("Executing Url -\n"+url)
        logging.info('executing url: ' + url)
        res = requests.get(url, auth=(self.username, self.password))
        return res
    #    print("Response is -\n"+res.text)
    #    resPayload = res.json()
    #    return resPayload

    def execute_post_service(self, url):
        # print("Executing Url -\n"+url)
        logging.info(' executing url: '+ url)
        res = requests.post(url, auth=(self.username, self.password))
        return res