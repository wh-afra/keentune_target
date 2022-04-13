import os
import re
import time
import subprocess

from target.common.config import Config
from target.common.system import sysCommand
from target.common.pylog import functionLog


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
    SUCCESS = True
    success_list = out.split('\n')
    failed_lsit  = err.split('\n')

    for param_name, param_info in param_list.items():
        for ele in success_list:
            match = re.match(r"({}) = (.+)".format(param_name), ele)
            if match is not None:
                result[param_name] = {
                    "value" : match.group(2),
                    "dtype" : param_info["dtype"],
                    "suc"   : True,
                    "msg"   : ele
                }
                break

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
                SUCCESS = False
                break

        if not result.__contains__(param_name):
            result[param_name] = {
                "value" : param_info["value"],
                "dtype" : param_info["dtype"],
                "suc"   : False,
                "msg"   : "can not find the param in output"
            }
            SUCCESS = False

    return SUCCESS, result


class Sysctl:
    name = "sysctl"
    get_cmd = "sysctl -n {name}"
    set_cmd = "sysctl -w {name}='{value}'"
    backup_file = os.path.join(
        Config.backup_dir, "{}_backup.conf".format(name))

    def __init__(self):
        super().__init__()

    @functionLog
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
                name=param_name.strip(),
                value=param_info['value']) + "\n"

        install_file = os.path.join(
            Config.backup_dir, "param_set_{}.sh".format(int(time.time())))
        with open(install_file, 'w') as f:
            f.write(cmd)

        _, out, err = _sysCommand("bash {}".format(install_file))
        suc, result = _parseResult(out, err, param_list)
        return suc, result

    @functionLog
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
        SUC = True
        for param_name, param_info in param_list.items():
            suc, param_value = sysCommand(
                command=self.get_cmd.format(name=param_name.strip()),
                cwd=Config.keentune_script_dir)

            if suc:
                result[param_name] = {
                    "value": param_value,
                    "dtype": param_info["dtype"],
                    "suc": True,
                    "msg": ""
                }
            else:
                SUC = False
                result[param_name] = {
                    "value": "",
                    "dtype": param_info["dtype"],
                    "suc": False,
                    "msg": param_value
                }
        return SUC, result

    @functionLog
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
        SUC = True
        backup_content = ""
        Errormsg = ""

        for param_name, param_info in param_list.items():
            suc, param_value = sysCommand(
                command=self.get_cmd.format(name=param_name.strip()),
                cwd=Config.keentune_script_dir)

            if not suc:
                SUC = False
                Errormsg += param_value + "\n"
                continue

            backup_content += "{name}={value}".format(
                name=param_name.strip(),
                value=param_value) + "\n"

        with open(self.backup_file, "w") as f:
            f.write(backup_content)

        if SUC:
            return True, self.backup_file
        else:
            return False, Errormsg

    @functionLog
    def rollback(self):
        """ Rollback to base configuration.

        Returns:
            suc (bool): if sucess to set parameters.
            msg (str) : error message or backup time.
        """
        if not os.path.exists(self.backup_file):
            return True, "Can not find backup file:{}".format(self.backup_file)

        suc, res = sysCommand("cat {} |while read line; do sysctl -w $line; done".format(self.backup_file))
        if suc:
            backup_time = time.asctime(time.localtime(
                os.path.getctime(self.backup_file)))
            os.remove(self.backup_file)
            return True, backup_time
        else:
            return False, res

@functionLog
def initialize():
    initialize_dir="/var/keentune/ServiceBackup"
    backup_file=os.path.join(initialize_dir, "sysctl.cnf")
    if os.path.exists(backup_file):
        return True, "backup file:{} exists, no need to backup again".format(backup_file)
    backup_cmd="sysctl -a > {}".format(backup_file)
    suc, out, err = _sysCommand(backup_cmd)
    if not suc:
        return False, "Backup parameters failed, reason:{}".format(err)
    return True, "Backup kernel parameters succeeded. Procedure"

