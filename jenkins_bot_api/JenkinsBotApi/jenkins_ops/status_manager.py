# import HttpRequestsUtility

from utils import http_utils, jenkins_utils, json_utils, xml_utils
import logging
import requests


class StatusManager:
    def __init__(self, jenkins_config):
        self.jenkins_util_obj = jenkins_utils.JenkinsUtil(jenkins_config)
        self.jenkins_endpoint = self.jenkins_util_obj.get_jenkins_endpoint()
        self.http_utils_obj = http_utils.HttpUtils(jenkins_config)
        self.jenkins_config = jenkins_config

    # retrieves pass fail count and result of given job
    # ex: what is status of master health check on qa ?
    # ans -{result: success, totalCount: 2, failCount:0, skipCount:0 }
    def get_job_status(self, env, job_name, job_type=None):
        logging.info("op type: get changeset details")
        if job_name is None:
            logging.info("Job Name is None")
            return "Please specify Job Name"

        job_url = self.jenkins_util_obj.get_job_name(job_name)
        # build_param = ""
        if job_type:
            build_param = "/api/xml?depth=1&xpath=//mavenModuleSet/build[action/parameter/value='"+env+"' and  action/parameter/value='"+job_type+"'][1]&wrapper=foreever"

        elif job_url in self.jenkins_config['env_job_mapping'][env].values():
            build_param = "/lastBuild/api/xml?tree=building,result"
        else:
            build_param = "/api/xml?depth=1&xpath=//mavenModuleSet/build[action/parameter/value='"+env+"'][1]&wrapper=foreever"
        url = self.jenkins_endpoint+job_url+build_param
        logging.info("url {}".format(url))
        return self.get_pass_fail_count(url)

    def get_pass_fail_count(self, url):
        try:
            resPayload = self.http_utils_obj.execute_get_service(url)
            #if resPayload.status_code == 200:
            if resPayload.status_code == requests.codes.ok:
                res_body = resPayload.content
                job_result_status = xml_utils.fetch_value_by_xpath(res_body, "//result/text()")
                totalCount = xml_utils.fetch_value_by_xpath(res_body, "//totalCount/text()")
                failCount = xml_utils.fetch_value_by_xpath(res_body, "//failCount/text()")
                skipCount = xml_utils.fetch_value_by_xpath(res_body, "//skipCount/text()")
                building = xml_utils.fetch_value_by_xpath(res_body, "//building/text()")
                if len(totalCount) != 0 and len(failCount) != 0 and len(skipCount) != 0:
                    return {"result": str(job_result_status[0]), "totalCount": str(totalCount[0]),
                            "failCount": str(failCount[0]), "skipCount": str(skipCount[0])}
                elif len(job_result_status) != 0:
                    return {"result": str(job_result_status[0])}
                elif len(building) != 0 and str(building[0]) == "true":
                    return {"result": "Running"}
                else:
                    return {} # No record Found
        except Exception as ex:
            logging.error(ex)
            return None

    # What is the status of QA Regression
    def get_job_status_by_job_type(self, env, job_type):
        default_upstream_job_name = "Master_HealthCheck"
        build_number = ""
        all_jobs_status = {}
        all_jobs_status, build_number = self.get_default_upstream_job_status_build_number(env, job_type)
        if build_number:
            downstream_job_url_list, downstream_job_name_list = self.get_downstream_jobs(default_upstream_job_name)
            i = 0
            if downstream_job_url_list and len(downstream_job_name_list) > 0:
                for downstream_job_url in downstream_job_url_list:
                    result_dict = self.get_job_status_by_upstream_job(downstream_job_url, default_upstream_job_name, build_number)
                    all_jobs_status.update({downstream_job_name_list[i]: result_dict})
                    i = i+1
        return all_jobs_status

    def get_job_status_by_upstream_job(self, job_url, upstream_job_name, upstream_job_build_number):
        job_url = job_url.replace("http://localhost:8080", self.jenkins_endpoint)
        build_param = "/api/xml?depth=1&xpath=//mavenModuleSet/build[action/cause/upstreamProject='"+upstream_job_name+"' and action/cause/upstreamBuild='"+upstream_job_build_number+"']&wrapper=forever"
        url = job_url + build_param
        return self.get_pass_fail_count(url)

    # getting list of all downstream projects
    def get_downstream_jobs(self, upstream_job_name):
        upstream_job_url = self.jenkins_util_obj.get_job_name(upstream_job_name)
        build_param = "/api/json?tree=downstreamProjects[name,url]"
        url = self.jenkins_endpoint+upstream_job_url+build_param
        try:
            resPayload = self.http_utils_obj.execute_get_service(url)
            # if resPayload.status_code == 200:
            if resPayload.status_code == requests.codes.ok:
                res_body = resPayload.json()
                downstream_job_url_list = json_utils.fetch_value_by_jsonPath(res_body, "$..url")
                downstream_job_name_list = json_utils.fetch_value_by_jsonPath(res_body, "$..name")
                return downstream_job_url_list, downstream_job_name_list
            else:
                return list()
        except Exception as ex:
            logging.error(ex)
            return None

    # get Master_HealthCheck Status with build number
    def get_default_upstream_job_status_build_number(self, env, job_type):
        default_upstream_job_name = "Master_HealthCheck"
        job_url = self.jenkins_util_obj.get_job_name(default_upstream_job_name)
        if job_type:
            build_param = "/api/xml?depth=1&xpath=//mavenModuleSet/build[action/parameter/value='" + env + "' and  action/parameter/value='" + job_type + "'][1]&wrapper=foreever"
        else:
            build_param = "/api/xml?depth=1&xpath=//mavenModuleSet/build[action/parameter/value='" + env + "'][1]&wrapper=foreever"
        url = self.jenkins_endpoint + job_url + build_param
        all_jobs_status = {}
        build_number = ""
        try:
            resPayload = self.http_utils_obj.execute_get_service(url)
            #if resPayload.status_code == 200:
            #if resPayload.codes.ok:
            if resPayload.status_code == requests.codes.ok:
                res_body = resPayload.content
                job_result_status = xml_utils.fetch_value_by_xpath(res_body, "//result/text()")
                build_number = xml_utils.fetch_value_by_xpath(res_body, "//number/text()")
                if len(build_number) != 0:
                    build_number = str(build_number[0])
                # Status of Master_HealthCheck itself
                totalCount = xml_utils.fetch_value_by_xpath(res_body, "//totalCount/text()")
                failCount = xml_utils.fetch_value_by_xpath(res_body, "//failCount/text()")
                skipCount = xml_utils.fetch_value_by_xpath(res_body, "//skipCount/text()")
                building = xml_utils.fetch_value_by_xpath(res_body, "//building/text()")
                if len(totalCount) != 0 and len(failCount) != 0 and len(skipCount) != 0:
                    all_jobs_status.update(
                        {default_upstream_job_name: {"result": str(job_result_status[0]),
                                                                    "totalCount": str(totalCount[0]),
                                                                    "failCount": str(failCount[0]),
                                                                    "skipCount": str(skipCount[0])}})
                    # return all_jobs_status # {"default_upstream_job_name": { "result": str(job_result_status[0]), "totalCount": str(totalCount[0]), "failCount": str(failCount[0]), "skipCount": str(skipCount[0])}}

                elif len(job_result_status) != 0:
                    all_jobs_status.update({"result": str(job_result_status[0])})
                elif len(building) != 0 and str(building[0]) == "true":
                    return {"result": "Running"}, build_number
                else:
                    return all_jobs_status, None  # No record Found
                return all_jobs_status, build_number
        except Exception as ex:
            logging.error(ex)
            return None, None