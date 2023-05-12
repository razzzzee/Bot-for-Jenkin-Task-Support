from utils import  http_utils, jenkins_utils
from .changeset_manager import ChangeSetManager
import logging
import requests

# jenkinsEndPoint="http://jenkins-master.westindia.cloudapp.azure.com:8080/"
logging.basicConfig(filename='../app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


class BuildPromoter:
    def __init__(self, jenkins_config):
        self.changeset_manager = ChangeSetManager(jenkins_config)
        self.jenkins_util_obj = jenkins_utils.JenkinsUtil(jenkins_config)
        self.http_util_obj = http_utils.HttpUtils(jenkins_config)
        self.jenkins_end_point = self.jenkins_util_obj.get_jenkins_endpoint()
        self.jenkins_config = jenkins_config

    # e.g. Deploy 154756 build to QA env
    def deploy_build(self, changeset, target_env):
        target_job_name = self.jenkins_config["env_job_mapping"][target_env]["Build_Promoter"]
        logging.info("op type: build deploy")
        logging.info("deploying {} changeset to {}".format(changeset, target_env))
        url_params = "/buildWithParameters?Changeset="+changeset

        if target_job_name and self.jenkins_end_point:
            try:
                url = self.jenkins_end_point+target_job_name+ url_params
                logging.info("invoking {}".format(url))
                res_payload = self.http_util_obj.execute_post_service(url)
                # logging.info("received status code:" + str(resPayload.status_code))
                #if res_payload.status_code == 201:
                if res_payload.status_code  == 201:
                    logging.info("build deployed successfully")
                    return True
                else:
                    logging.info("failed to deploy build")
                    return False
            except Exception as e:
                logging.error(e)
                return False

    # e.g. Deploy Dev build to QA env
    def deploy_build_without_changeset(self, source_env, target_env):
        logging.info("op type: build deploy without changeset")
        logging.info("deploying build from {} to {} env".format(source_env, target_env))
        changeset = self.changeset_manager.get_lastsuccessfulbuild_changeset_details(source_env)
        return self.deploy_build(changeset, target_env)

    # To deploy on Dev, Just have to trigger Compile_Publish job
    def deploy_build_on_dev(self, target_env):
        logging.info("op type: build deploy on target environment")
        logging.info("deploying build on dev")
        target_job_name = self.jenkins_config["env_job_mapping"][target_env]["Build_Promoter"]
        url_param = "/Build"
        url = self.jenkins_end_point + target_job_name + url_param
        logging.info("invoking {}".format(url))
        res_payload = self.http_util_obj.execute_post_service(url)
        if res_payload.status_code == requests.codes.ok:
            logging.info("triggered build deployment on dev")
            return True
        else:
            logging.info("failed to trigger build deployment")
            return False
