import logging


class JenkinsUtil:
    def __init__(self, jenkins_config):
        self.jenkins_config = jenkins_config

    # @staticmethod
    def get_job_name(self, source_env):
        if source_env and self.jenkins_config is not None:
            mapped_job_name = self.jenkins_config['env_job_mapping'][source_env]
            return mapped_job_name
        else:
            logging.info("{} environment not found".format(source_env))
            return None

    # @staticmethod
    def get_jenkins_endpoint(self):
        if self.jenkins_config is not None:
            return self.jenkins_config['host_config']['jenkins_endpoint']
        else:
            return None