from utils import jenkins_utils, http_utils
import logging
import requests
import json


class JobInfoManager:

    def __init__(self, jenkins_config):
        self.jenkins_util_obj = jenkins_utils.JenkinsUtil(jenkins_config)
        self.jenkins_endpoint = self.jenkins_util_obj.get_jenkins_endpoint()
        self.http_utils_obj = http_utils.HttpUtils(jenkins_config)

    # get last execution info of given job
    def get_last_running_job_info(self, job_name):
        try:
            job_last_info_url = "{}/job/{}/api/json?tree=lastBuild[building,id,timestamp]".format(self.jenkins_endpoint, job_name)
            res = self.http_utils_obj.execute_get_service(job_last_info_url)
            if res and res.status_code == requests.codes.ok:
                json_content= res.json()
                #res_json = json.loads(json_content)
                if json_content and len(json_content) > 0:
                    job_id = json_content['lastBuild']['id']
                    job_run_status = json_content['lastBuild']['building']
                    return job_id, job_run_status
                else:
                    return None, None
        except Exception as ex:
            logging.error("error occurred while fetching last execution info of {} job".format(job_name))
            logging.error(ex)
            return None, None





