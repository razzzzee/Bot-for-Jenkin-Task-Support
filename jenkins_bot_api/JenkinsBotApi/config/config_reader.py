import json
from os import path
import logging

logging.basicConfig(filename='../app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


class ConfigReader:
    def __init__(self):
        self.config_path = "../jenkins_config.json"
        self.jekins_config = None

    '''
    reads configuration from jenkins_config.json
    '''
    def read_config(self):
        try:
            if path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.jenkins_config = json.load(f)
                    logging.debug("configuration read: {}".format(json.dumps(self.jenkins_config)))
                    return True
            else:
                # print("config file does not exists, please ensure its present")
                logging.info("configuration file not present")
                return False
        except Exception as ex:
            logging.error(ex)
            return False


    def print_config(self):
        print(json.dumps(self.jenkins_config))

#
# def main():
#     configreader = ConfigReader()
#     configreader.read_config()
#     configreader.print_config()
#
#
# if __name__ == "__main__":
#     main()
