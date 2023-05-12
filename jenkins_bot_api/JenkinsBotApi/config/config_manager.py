from config.config_reader import ConfigReader


class ConfigManager:
    def __init__(self):
        self.jenkins_config = None

    def initialize_config(self):
        if self.jenkins_config is None:
            config_reader = ConfigReader()
            config_status = config_reader.read_config()
            if config_status:
                self.jenkins_config = config_reader.jenkins_config
                return config_status
