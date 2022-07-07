import os
import logging

from configparser import ConfigParser

LOGLEVEL = {
    "DEBUG"     : logging.DEBUG,
    "INFO"      : logging.INFO,
    "WARNING"   : logging.WARNING,
    "ERROR"     : logging.ERROR
}

class Config:
    conf_file_path = "/etc/keentune/conf/target.conf"
    conf = ConfigParser()
    conf.read(conf_file_path)

    KEENTUNE_HOME       = conf['agent']['KEENTUNE_HOME']
    KEENTUNE_WORKSPACE  = conf['agent']['KEENTUNE_WORKSPACE']
    ORIGINAL_CONF_PATH  = conf['agent']['ORIGINAL_CONF']
    AGENT_PORT          = conf['agent']['AGENT_PORT']

    print("KeenTune Home: {}".format(KEENTUNE_HOME))
    print("KeenTune Workspace: {}".format(KEENTUNE_WORKSPACE))
    print("Listening port: {}".format(AGENT_PORT))

    KEENTUNE_SCRIPT_PATH = os.path.join(KEENTUNE_HOME, 'script')
    BACNUP_PATH         = os.path.join(KEENTUNE_WORKSPACE, "backup")

    for _path in [
        KEENTUNE_WORKSPACE, KEENTUNE_SCRIPT_PATH, BACNUP_PATH, ORIGINAL_CONF_PATH]:
        if not os.path.exists(_path):
            os.makedirs(_path)

    LOGFILE_PATH = conf['log']['LOGFILE_PATH']
    _LOG_DIR = os.path.dirname(LOGFILE_PATH)
    if not os.path.exists(_LOG_DIR):
        os.makedirs(_LOG_DIR)
        os.system("chmod 0755 {}".format(_LOG_DIR))

    CONSOLE_LEVEL       = LOGLEVEL[conf['log']['CONSOLE_LEVEL']]
    LOGFILE_LEVEL       = LOGLEVEL[conf['log']['LOGFILE_LEVEL']]
    LOGFILE_INTERVAL    = int(conf['log']['LOGFILE_INTERVAL'])
    LOGFILE_BACKUP_COUNT= int(conf['log']['LOGFILE_BACKUP_COUNT'])
