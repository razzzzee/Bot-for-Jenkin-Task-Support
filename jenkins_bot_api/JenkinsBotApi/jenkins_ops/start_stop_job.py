from utils import jenkins_utils, http_utils
import logging
from  jenkins_ops import job_info_manager
import requests

class StartStopJenkinsJob:
    def __init__(self, jenkins_config):
        self.jenkins_config = jenkins_config
        self.jenkins_util_obj = jenkins_utils.JenkinsUtil(jenkins_config)
        self.jenkins_endpoint = self.jenkins_util_obj.get_jenkins_endpoint()
        self.http_utils_obj = http_utils.HttpUtils(jenkins_config)

    def stop_job(self, job_name):
        info_manager = job_info_manager.JobInfoManager(self.jenkins_config)
        job_id, running_status =info_manager.get_last_running_job_info(job_name)
        response_text = None
        if job_id:
            if running_status:
                job_stop_url = "{}/job/{}/{}/stop".format(self.jenkins_endpoint, job_name,job_id)
                try:
                    res = self.http_utils_obj.execute_post_service(job_stop_url)
                    if res and res.status_code == res.codes.ok:
                        status_response = res.json()
                        logging.info("stopped {} job with id {}".format(job_name, job_id))
                        response_text = "stopped {} job with id {}".format(job_name, job_id)
                        #return response_text, True
                except Exception as ex:
                    logging.error(ex)
                    logging.info("failed to stop {} job with id: {}".format(job_name, job_id))
                    response_text = "failed to stop {} job with id: {}".format(job_name, job_id)
                    #return response_text, False
            else:
                logging.info("{} job is not running".format(job_name))
                response_text = "{} job is not running".format(job_name)
                #return response_text, False
        else:
            logging.info("failed to fetch job execution status for {} job".format(job_name))
            response_text = "failed to fetch job execution status for {} job".format(job_name)
            # return response_text, False
        return response_text

    def start_job(self, env_name, job_name, job_type=None):
        try:
            job_url = self.jenkins_util_obj.get_job_name(job_name)
            url = "{}{}/buildWithParameters?Environment={}".format(self.jenkins_endpoint, job_url, env_name)
            # test_suite_url = "{}job/Master_HealthCheck/buildWithParameters?Environment={}&TestType={}".format(
            #     self.jenkins_endpoint, env, test_suite_name)
            res_obj = self.http_utils_obj.execute_post_service(url)
            if res_obj and res_obj.status_code == 201:
                logging.info("triggered job {} on {} env".format(job_name, env_name))
                return True
        except:
            logging.info("failed to trigger job: {} on {} env".format(job_name, env_name))
            return False
