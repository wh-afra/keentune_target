import os
import re
import time
import subprocess

from agent.common.config import Config
from agent.common.system import sysCommand
from agent.common.pylog import logger

def _sysCommand(cmd: str):
    result = subprocess.run(
        cmd,
        shell=True,
        close_fds=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    suc = (result.returncode == 0)
    out = result.stdout.decode('UTF-8', 'strict').strip()
    err = result.stderr.decode('UTF-8', 'strict').strip()
    return suc, out, err


def _parseResult(out: str, err: str, param_list: list):
    result = {}
    SUCCESS = False
    success_list = out.split('\n')
    failed_lsit  = err.split('\n')

    for param_name, param_info in param_list.items():
        if result.__contains__(param_name):
            continue
        
        for ele in failed_lsit:
            match = re.search(param_name, ele)
            if match is not None:
                result[param_name] = {
                    "value" : param_info["value"],
                    "dtype" : param_info["dtype"],
                    "suc"   : False,
                    "msg"   : ele
                }
                logger.warning("Failed to set knobs {}: {}".format(param_name, ele))
                break

        for ele in success_list:
            match = re.match(r"({}) = (.+)".format(param_name), ele)
            if match is not None:
                result[param_name] = {
                    "value" : match.group(2),
                    "dtype" : param_info["dtype"],
                    "suc"   : True,
                    "msg"   : ele
                }
                logger.debug("set knobs {}: {}".format(param_name,ele))
                SUCCESS = True
                break

        if not result.__contains__(param_name):
            result[param_name] = {
                "value" : param_info["value"],
                "dtype" : param_info["dtype"],
                "suc"   : False,
                "msg"   : "can not find the param in output"
            }
            logger.warning("Failed to set knobs {}: can not find it in output".format(param_name))

    return SUCCESS, result


class Sysctl:
    name = "sysctl"
    get_cmd = "sysctl -n {name}"
    set_cmd = "sysctl -w {name}='{value}'"
    backup_file = os.path.join(
        Config.BACNUP_PATH, "{}_backup.conf".format(name))

    def __init__(self):
        super().__init__()

    def setParamAll(self, param_list: dict):
        """ Set parameters of sysctl.

        Args:
            param_list (dict): parameter dict. e.g. 
            {
                [parameter_name]: {
                    'dtype': [parameter_dtype], 
                    'value': [parameter_value]
                },
                ...
            }

        Returns:
            suc (bool): if sucess to set parameters.
            result (dict): parameter setting result. e.g. 
            {
                [parameter_name]: {
                    'dtype': [parameter_dtype], 
                    'value': [parameter_value],
                    'suc'  : [if success to set the parameter],
                    'msg'  : [error message]
                },
                ...
            }
        """
        cmd = ""
        for param_name, param_info in param_list.items():
            if param_info['value'] == "":
                continue
            cmd += self.set_cmd.format(
                name  = param_name.strip(),
                value = param_info['value']) + "\n"

        install_file = os.path.join(
            Config.BACNUP_PATH, 
            "param_set_{}.sh".format(int(time.time()))
        )
        logger.info("Generating knobs setting script: {}".format(install_file))
        with open(install_file, 'w') as f:
            f.write(cmd)

        logger.info("Run knobs setting script: bash {}".format(install_file))
        _, out, err = _sysCommand("bash {}".format(install_file))

        logger.info("parse result of setting script.")
        suc, result = _parseResult(out, err, param_list)

        return suc, result


    def getParamAll(self, param_list: dict):
        """ Get parameter value of sysctl.

        Args:
            param_list (dict): parameter dict. e.g. 
            {
                [parameter_name]: {
                    'dtype': [parameter_dtype], 
                },
                ...
            }

        Returns:
            suc (bool): if sucess to set parameters.
            result (dict): parameter setting result. e.g. 
            {
                [parameter_name]: {
                    'dtype': [parameter_dtype], 
                    'value': [parameter_value],
                    'suc'  : [if success to set the parameter],
                    'msg'  : [error message]
                },
                ...
            }        
        """
        result = {}
        SUCCESS = False
        for param_name, param_info in param_list.items():
            suc, param_value = sysCommand(
                command = self.get_cmd.format(name=param_name.strip()),
                cwd     = Config.KEENTUNE_SCRIPT_PATH)

            if suc:
                result[param_name] = {
                    "value": param_value,
                    "dtype": param_info["dtype"],
                    "suc": True,
                    "msg": ""
                }
                SUCCESS = True
            else:
                result[param_name] = {
                    "value": "",
                    "dtype": param_info["dtype"],
                    "suc": False,
                    "msg": param_value
                }
                logger.warning("Failed to read knobs {}: {}".format(param_name, param_value))
            
        return SUCCESS, result


    def backup(self, param_list: dict):
        """ Save sysctl parameter value to backup file.

        Generating backup file as .sh

        Args:
            param_list (dict): parameter to backupt. e.g. 
            {
                [parameter_name]: {
                    'dtype': [parameter_dtype], 
                },
                ...
            }

        Returns:
            suc (bool): if sucess to set parameters.
            msg (str) : error message or backup file path.
        """
        SUCCESS = True
        backup_content = ""
        Errormsg = ""

        for param_name, _ in param_list.items():
            suc, param_value = sysCommand(
                command = self.get_cmd.format(name=param_name.strip()),
                cwd     = Config.KEENTUNE_SCRIPT_PATH)
            if not suc:
                SUCCESS = False
                Errormsg += param_value + "\n"
                logger.warning("Failed to read knobs value {}: {}".format(param_name, param_value))
                continue
            backup_content += "{name}={value}".format(
                name  = param_name.strip(),
                value = param_value) + "\n"

        logger.info("Generating rollback script:{}".format(self.backup_file))
        with open(self.backup_file, "w") as f:
            f.write(backup_content)

        if SUCCESS:
            return True, self.backup_file
        else:
            return False, Errormsg


    def rollback(self):
        """ Rollback to base configuration.

        Returns:
            suc (bool): if sucess to set parameters.
            msg (str) : error message or backup time.
        """
        if not os.path.exists(self.backup_file):
            return True, "Can not find backup file:{}".format(self.backup_file)

        suc, res = sysCommand("IFS='';cat {} |while read line; do sysctl -w $line; done".format(self.backup_file))
        if suc:
            backup_time = time.asctime(time.localtime(
                os.path.getctime(self.backup_file)))
            logger.info("Rollback to backup time: {}".format(backup_time))
            os.remove(self.backup_file)
            return True, backup_time

        else:
            logger.error("Failed to rollback: {}".format(res))
            return False, res

    def originalConfig(self, action):
        backup_file = os.path.join(Config.ORIGINAL_CONF_PATH, "sysctl.cnf")

        if action == "backup":
            if os.path.exists(backup_file):
                return True, "backup file:{} exists, no need to backup again".format(backup_file)

            suc, _, err = _sysCommand("sysctl -a > {}".format(backup_file))
            if not suc:
                return False, "Backup parameters failed, reason:{}".format(err)

            return True, "Backup kernel parameters succeeded. Procedure"

        elif action == "rollback":
            if not os.path.exists(backup_file):
                return True, "No backup file was found"

            suc, _, err = _sysCommand("sysctl -p {}".format(backup_file))
            if not suc:
                return False, "Failed to rollback kernel parameters. Procedure, reason:{}".format(err)

            os.remove(backup_file)
            return True, "The rollback of kernel parameters succeeded. Procedure"