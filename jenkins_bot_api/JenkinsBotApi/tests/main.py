from config.config_reader import ConfigReader
from jenkins_ops.build_promoter import BuildPromoter
import jenkins


def main():
    configreader = ConfigReader()
    configreader.read_config()
    endpoint = configreader.jenkins_config['host_config']['jenkins_endpoint']
    username = configreader.jenkins_config['host_config']['username']
    password = configreader.jenkins_config['host_config']['password']
    jenkins_obj = jenkins.Jenkins(endpoint, username, password)
    user_info = jenkins_obj.get_whoami()
    print(user_info)

    # buildpromoter = BuildPromoter(configreader)
    # buildpromoter.deploy_build_without_changeset("Dev", "QA")
    #c = deploy_build_without_changeset("Dev", "QA")
    # configreader.read_config()
    # configreader.print_config()


if __name__ == "__main__":
    main()
