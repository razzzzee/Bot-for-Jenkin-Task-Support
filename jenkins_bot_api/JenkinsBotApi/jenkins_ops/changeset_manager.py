# import HttpRequestsUtility
from utils import http_utils, jenkins_utils, json_utils
import logging
import requests
# jenkinsEndPoint = "http://jenkins-master.westindia.cloudapp.azure.com:8080/"


# def get_job_name(env):
#    if env in "Dev":
#        return get_changeset_details('Dev', 'job/Deploy_Dev')
#    if env in "QA":
#        return get_changeset_details('QA', 'job/Deploy_QA')
#    if env in "STG":
#        return get_changeset_details('STG', 'job/Deploy_STG')

class ChangeSetManager:
    def __init__(self, jenkins_config):
        self.jenkins_util_obj = jenkins_utils.JenkinsUtil(jenkins_config)
        self.jenkins_endpoint = self.jenkins_util_obj.get_jenkins_endpoint()
        self.http_utils_obj = http_utils.HttpUtils(jenkins_config)
        self.jenkins_config = jenkins_config

    # get changeset details of last successful build on given environment
    def get_changeset_details(self, env, job_name=None):
        logging.info("op type: get changeset details")
        if job_name is None:
            job_name = self.jenkins_config["env_job_mapping"][env]["Deploy"]
        lastSuccessfulBuild = self.get_lastsuccessfulbuild_changeset_details(env, job_name)
        lastBuild = self.get_lastbuild_changeset_details(env, job_name)
        logging.info("last success build:{} , last build status: {}".format(lastSuccessfulBuild, lastBuild))
        if lastBuild == lastSuccessfulBuild:
            return lastBuild
        else:
            #return {"latestBuild": lastBuild, "lastSuccessfulBuild":lastSuccessfulBuild }
            return "latest Failed Build : {}, last Successful Build: {}".format(lastBuild, lastSuccessfulBuild)

    # fetch lastSuccessfulBuild deployed on env
    def get_lastsuccessfulbuild_changeset_details(self, env, job_name=None):
        logging.info("op type: get last successful build details")
        if job_name is None:
            job_name = self.jenkins_config["env_job_mapping"][env]["Deploy"]
        return self.get_latest_changeset_details(env, job_name, buildParam='lastSuccessfulBuild')

    # fetch latest build(success/failed/aborted) on env
    def get_lastbuild_changeset_details(self, env, job_name=None):
        logging.info("op type: get last changeset details")
        if job_name is None:
            job_name = self.jenkins_config["env_job_mapping"][env]["Deploy"]
        return self.get_latest_changeset_details(env, job_name, buildParam='lastBuild')

    # retrieve latest changeset details
    def get_latest_changeset_details(self, env, job_name=None, buildParam= 'lastBuild'):
        if job_name is None:
            job_name = self.jenkins_config["env_job_mapping"][env]["Deploy"]

        # xml_url = "/lastSuccessfulBuild/api/xml?tree=actions[parameters[name,value]]&xpath=freeStyleBuild/action/parameter[name='Changeset']/value"

        urlParam = "/" + buildParam + "/api/json?tree=actions[parameters[name,value]]"
        url = self.jenkins_endpoint + job_name + urlParam
        logging.info("triggering url: {}".format(url))
        try:
            res_payload = self.http_utils_obj.execute_get_service(url)
            if res_payload.status_code == requests.codes.ok:
                result = json_utils.fetch_value_by_jsonPath(res_payload.json(), "$..parameters[?(@.name=='Changeset')].value")
                # print("Changeset is : " + str(result))
                if result and len(result) >0:
                    logging.info("fetched {} details successsfully".format(result[0]))
                    return str(result[0])
                else:
                    return None
        except Exception as ex:
            logging.error(ex)
            logging.info("failed to get lastest changeset details")
            return None

# c = get_changeset_details("Dev")s
