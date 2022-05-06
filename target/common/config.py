import logging
import os
from configparser import ConfigParser

LOGLEVEL = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR
}

class Config:
    conf_file_path = "/etc/keentune/conf/target.conf"
    conf = ConfigParser()
    conf.read(conf_file_path)

    keentune_home = conf['home']['keentune_home']
    keentune_workspace = conf['home']['keentune_workspace']
    print("KeenTune Home: {}".format(keentune_home))
    print("KeenTune Workspace: {}".format(keentune_workspace))

    keentune_conf_dir = os.path.join(keentune_home, 'conf')
    keentune_script_dir = os.path.join(keentune_home, 'script')
    target_port = conf['target']['target_port']

    if not os.path.exists(keentune_script_dir):
        os.makedirs(keentune_script_dir)

    if not os.path.exists(keentune_workspace):
        os.makedirs(keentune_workspace)

    backup_dir = os.path.join(keentune_workspace, "backup")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)


    logfile_path = conf['log']['logfile_path']
    log_dir = os.path.dirname(logfile_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    console_level = LOGLEVEL[conf['log']['console_level']]
    logfile_level = LOGLEVEL[conf['log']['logfile_level']]
    logfile_interval = int(conf['log']['logfile_interval'])
    logfile_backup_count = int(conf['log']['logfile_backup_count'])
