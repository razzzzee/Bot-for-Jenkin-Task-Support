import logging
from config.config_manager import ConfigManager
from jenkins_ops.changeset_manager import ChangeSetManager
from jenkins_ops.build_promoter import BuildPromoter
from jenkins_ops.start_stop_job import  StartStopJenkinsJob
from jenkins_ops.status_manager import StatusManager
from jenkins_ops.test_trigger import TestTrigger
logging.basicConfig(filename='../app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

config_manager = None


class BotActions:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.build_promoter = None
        self.changeset_manager = None
        if self.config_manager.initialize_config():
            self.build_promoter = BuildPromoter(self.config_manager.jenkins_config)
            self.changeset_manager = ChangeSetManager(self.config_manager.jenkins_config)
            self.start_stop_jenkins_job =  StartStopJenkinsJob(self.config_manager.jenkins_config)
            self.status_manager = StatusManager(self.config_manager.jenkins_config)
            self.test_trigger = TestTrigger(self.config_manager.jenkins_config)
            logging.info("initialized changeset manager successfully")
        else:
            logging.info('failed to initialize changeset manager')

    # trigger build with given data
    def trigger_build(self, data):
        job_name = data['queryResult']['parameters']['job_name']
        environment = data['queryResult']['parameters']['environment']
        # self.test_trigger.trigger_test_suite(environment,)
        self.start_stop_jenkins_job.start_job(environment, job_name)
        logging.info("triggered {} job on {} environment".format(job_name, environment))
        return "triggered {} job on {} environment successfully".format(job_name, environment)

    # promotes/deploys job on specific environment
    def promote_build(self, data):
        source_env = data['queryResult']['parameters']['src_env']
        target_env = data['queryResult']['parameters']['dst_env']
        changeset = data['queryResult']['parameters']['changeset']

        if source_env and target_env and changeset:
            logging.info("promoting change set {} from {} env to {} env".format(changeset, source_env, target_env))
            build_promote_status = self.build_promoter.deploy_build(changeset, target_env)
            if build_promote_status:
                return "promoting change set {} to {} env".format(changeset, target_env)
            else:
                return "promotion of changeset {} to {} env failed".format(changeset, target_env)

        elif changeset and target_env:
            logging.info("promoting change set {} to {} env".format(changeset, target_env))
            build_promote_status = self.build_promoter.deploy_build(changeset, target_env)
            logging.info("build promotion status : {}".format(str(build_promote_status)))
            if build_promote_status:
                return "promoting change set {} to {} env".format(changeset, target_env)
            else:
                return "promotion of changeset {} to {} env failed".format(changeset, target_env)

        elif source_env and target_env:
            logging.info("promoting build from {} env to {} env".format(source_env, target_env))
            build_promote_status = self.build_promoter.deploy_build_without_changeset(source_env, target_env)
            logging.info("build promotion status : {}".format(str(build_promote_status)))
            if build_promote_status:
                return "successfully triggered build promotion from {} env to {} env".format(source_env, target_env)
            else:
                return "failed to promote build from {} env to {} env".format(source_env, target_env)

        elif target_env:
            if target_env == "Dev":
                logging.info("promoting build on {} env".format(changeset, target_env))
                build_promote_status = self.build_promoter.deploy_build_on_dev(target_env)
                logging.info("build promotion status : {}".format(str(build_promote_status)))
                if build_promote_status:
                    return "successfully promoted build on {} env".format(target_env)
                else:
                    return "failed to promote build on {} env failed".format(target_env)
            else:
                return "please specify changeset no. for build promotion {} env".format(target_env)


    # aborts job mentioned by name
    def abort_job_by_name(self, data):
        env_name = data['queryResult']['parameters']['environment']
        job_name = data['queryResult']['parameters']['job_name']
        logging.info("aborting {} on {} env".format(env_name, job_name))
        response_text = self.start_stop_jenkins_job.stop_job(job_name)
        return response_text
        # return "aborting {} on {} env".format(env_name, job_name)

    # retrieves changeset details
    def retrieve_changeset_details(self, data):
        env_name = data['queryResult']['parameters']['environment']
        logging.info("fetching latest change set on {} env".format(env_name))
        # return "latest changeset on {} env is 123456.".format(env_name)
        if self.changeset_manager:
            #changeset_details = self.changeset_manager.get_latest_changeset_details(env=env_name)
            changeset_details = self.changeset_manager.get_changeset_details(env=env_name)
            if changeset_details:
                logging.info("fetching latest change set on {} env is {}".format(env_name, changeset_details))
                return "changeset on {} env is {}".format(env_name, changeset_details)
            else:
                return "could not find any changeset on {}".format(env_name)
        else:
            return "failed to initialise changeset Manger"

    # retrieves job status by name
    # {result: success, totalCount: 2, failCount:0, skipCount:0 }
    def retrieve_job_status(self, data):
        job_type = None
        env_name = data['queryResult']['parameters']['environment']
        job_name = data['queryResult']['parameters']['job_name']
        if 'job_type' in data['queryResult']['parameters']:
            job_type = data['queryResult']['parameters']['job_type']

        if env_name and job_name and job_type:
            logging.info("retrieving execution status of {} type of {} job on {} environment".format(job_type, job_name, env_name))
            status_result = self.status_manager.get_job_status(env_name, job_name, job_type)
            response_text = ""
            for job_name, job_res in status_result.items():
                response_text += "\n for {} job on {} env, result status: {}, total test count: {}, fail count: {}, skip count: {}".format(
                    job_name, env_name, job_res['result'], job_res['totalCount'], job_res['failCount'],
                    job_res['skipCount'])
            ##return "status of {} jobs on {} env is good".format(job_type, env_name)
            return response_text

        if env_name and job_name:
            logging.info("retrieving execution status of {} job on {} environment".format(job_name, env_name))
            status_result = self.status_manager.get_job_status(env_name, job_name)
            logging.info("status result :{}".format(status_result))
            if status_result and type(status_result)== dict and len(status_result) >0:
                if len(status_result) == 4:
                    return "for {} job on {} env, result status: {}, total test count: {}, fail count: {}, skip count: {}".format(job_name, env_name, status_result['result'], status_result['totalCount'], status_result['failCount'],status_result['skipCount'])
                elif len(status_result) == 1:
                    return "result status: {}".format(status_result['result'])
            else:
                return "failed to obtain status of {} job on {} env".format(job_name, env_name)
        elif env_name and job_type:
            logging.info("retrieving execution status of {} jobs on {} env ".format(job_type, env_name))
            res = self.status_manager.get_job_status_by_job_type(env_name, job_type)
            logging.info('execution status response: ' + str(res))
            response_text = ""
            if res and len(res) > 0:
                for job_name, job_res in res.items():
                    if job_res and len(job_res) == 4:
                        response_text +="\nfor {} job on {} env, result status: {}, total test count: {}, fail count: {}, skip count: {}".format(
                            job_name, env_name, job_res['result'], job_res['totalCount'], job_res['failCount'], job_res['skipCount'])
                    elif len(job_res) == 1:
                        return "result status: {}".format(job_res['result'])
                    else:
                        response_text += "\n {} job not triggered on {} env".format(job_name, env_name)
            else:
                response_text = "unable to fetch status of {} job type on {} env".format(job_type, env_name)
            return response_text
        elif env_name:
            logging.info("retrieving execution status of ")
            res = self.status_manager.get_job_status(env_name, None)
            logging.info('response of status check is' + str(res))
            response_text = ""
            if type(res) == dict and res and len(res) > 0:
                for job_name, job_res in res.items():
                    if job_res and len(job_res) == 4:
                        response_text += "for {} job on {} env, result status: {}, total test count: {}, fail count: {}, skip count: {}".format(
                            job_name, env_name, job_res['result'], job_res['totalCount'], job_res['failCount'],
                            job_res['skipCount'])
                    else:
                        response_text += "\n {} job not triggered on {} env".format(job_name, env_name)
            else:
                response_text = "unable to fetch status of {} env".format(job_type)
            return response_text

    # retrieves job status by type
    # def retrieve_job_status_by_type(self, data):
    #     env_name = data['queryResult']['parameters']['environment']
    #     job_type = data['queryResult']['parameters']['job_type']
    #     logging.info("retrieving execution status of {} jobs on {} env ".format(job_type, env_name))
    #     res = self.status_manager.get_job_status_by_job_type(env_name, job_type)
    #     response_text =""
    #     for job_name, job_res in res.items():
    #         response_text +="\n for {} job on {} env, result status: {}, total test count: {}, fail count: {}, skip count: {}".format(
    #             job_name, env_name, job_res['result'], job_res['totalCount'], job_res['failCount'], job_res['skipCount'])
    #     ##return "status of {} jobs on {} env is good".format(job_type, env_name)
    #     return response_text

    # # retrieve pass fail count
    # def retrieve_pass_fail_count(self, data):
    #     env_name = data['queryResult']['parameters']['environment']
    #     job_name = data['queryResult']['parameters']['job_name']
    #     job_success_criteria = data['queryResult']['parameters']['job_success_status']
    #     logging.info("fetching {} count for {} job on {} env".format(job_success_criteria, job_name, env_name))
    #     pass_count = 10
    #     fail_count = 0
    #     if job_success_criteria == "pass":
    #         return "Number of tests passing on {} env for {} job are {}".format(env_name, job_name, str(pass_count))
    #     elif job_success_criteria == "fail":
    #         return "Number of tests failing on {} env for {} job are {}".format(env_name, job_name, str(fail_count))
    #     elif job_success_criteria is None:
    #         return "On env: {} for {} job Number of tests passed: {}, tests failed: {}".format(env_name, job_name, str(pass_count), str(fail_count))


    # invokes test suite on given environment
    def invoke_test_suite(self, data):
        env_name = data['queryResult']['parameters']['environment']
        job_type = data['queryResult']['parameters']['job_type']
        logging.info("fetching execution status of {} job on {} env".format(job_type, env_name))
        status = self.test_trigger.trigger_test_suite(env_name, job_type)
        if status:
            return "invocation of {} test suite on {} env successfully done".format(job_type, env_name)
        else:
            return "failed to trigger {} test suite on {} env".format(job_type, env_name)

    # reruns given job on given environment
    def rerun_job(self, data):
        env_name = data['queryResult']['parameters']['environment']
        job_name = data['queryResult']['parameters']['job_name']
        logging.info("re triggering {} job on {} env".format(job_name, env_name))
        return "re triggered {} job on {} env".format(job_name, env_name)