from utils import jenkins_utils, http_utils
import logging

'''
triggers test suite on given environment
'''

class TestTrigger:

    def __init__(self, jenkins_config):
        self.jenkins_util_obj = jenkins_utils.JenkinsUtil(jenkins_config)
        self.jenkins_endpoint = self.jenkins_util_obj.get_jenkins_endpoint()
        self.http_utils_obj = http_utils.HttpUtils(jenkins_config)

    # triggers a job on given env
    def trigger_test_suite(self, env, test_suite_name):
        try:
            test_suite_url = "{}job/Master_HealthCheck/buildWithParameters?Environment={}&TestType={}".format(self.jenkins_endpoint, env, test_suite_name)
            res_obj = self.http_utils_obj.execute_post_service(test_suite_url)
            if res_obj and res_obj.status_code == 201:
                logging.info("triggered test suite {} on {} env".format(test_suite_name, env))
                return True
        except:
                logging.info("failed to trigger test suite: {} on {} env".format(test_suite_name, env))
                return False