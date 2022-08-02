import os
import time

from agent.common.config import Config
from agent.common.pylog import functionLog
from agent.common.system import sysCommand

class Mycnf:
    mycnf="/etc/my.cnf"
    get_cmd = "cat /etc/my.cnf |grep -w {name} | tail -n1 | awk -F'=' '{{print$2}}'"
    set_cmd = "echo {name}={value} >> /etc/my.cnf"
    get_flag = "cat /etc/my.cnf  |grep -w {name} | tail -n1 |wc -L |awk '{{if (sum=$(wc -L \"{name}\") && $0==$sum) print \"ON\";else print \"OFF\"}}'"
    set_flag = "echo {name} >> /etc/my.cnf"

    def __init__(self):
        super().__init__()

    @functionLog
    def _afterParamSet(self):
        return True, "unnecessary"

    @functionLog
    def _beforeParamSet(self):
        mycnfData="[client-server]\n!includedir /etc/my.cnf.d\n[mysqld]\n"
        with open(os.path.join(self.mycnf),"w") as f:
            f.write(mycnfData)
        return True, ""

    @functionLog
    def _setParam(self, param_name: str, param_info: dict):
        set_cmd = self.set_cmd.format(
            name=param_name.strip(),
            value=param_info['value'])

        return sysCommand(
            command = set_cmd,
            cwd = Config.KEENTUNE_SCRIPT_PATH)

    @functionLog
    def _getParam(self, param_name: str):
        get_cmd = self.get_cmd.format(name=param_name.strip())

        return sysCommand(
            command = get_cmd,
            cwd = Config.KEENTUNE_SCRIPT_PATH)

    @functionLog
    def _setFlag(self, param_name: str):
        set_flag = self.set_flag.format(name = param_name.strip())
        print("set_flag:",set_flag)

        return sysCommand(command = set_flag)

    @functionLog
    def _getFlag(self, param_name: str):
        get_flag = self.get_flag.format(name = param_name.strip())
        print("get_flag:",get_flag)

        return sysCommand(command = get_flag)

    @functionLog
    def setParamAll(self, param_list: dict):
        for param_name, param_info in param_list.items():
            if param_info['value'] != "":
                suc,res = self._beforeParamSet()
                if not suc:
                    return False, res
                break
            else:
                continue

        result = {}
        for param_name, param_info in param_list.items():
            if param_info['value'] == "":
                continue

            if param_name == "skip_ssl":
                if param_info["value"] == "ON":
                    suc, res = self._setFlag(param_name)
            else:
                suc, res = self._setParam(param_name, param_info)

            result[param_name] = {
                "value": param_info["value"],
                "dtype": param_info["dtype"],
                "suc": suc,
                "msg": res
            }

        suc,res = self._afterParamSet()
        if not suc:
            return False, res

        return True, result

    @functionLog
    def getParamAll(self, param_list: dict):
        result = {}
        SUC = True
        for param_name, param_info in param_list.items():
            if param_name == "skip_ssl":
                suc, res = self._getFlag(param_name)
            else:
                suc, res = self._getParam(param_name)

            if suc:
                result[param_name] = {
                    "value": res,
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
                    "msg": res
                }
        return SUC, result

    @functionLog
    def rollback(self):
        backup_content = ""
        backup_file = os.path.join(Config.BACNUP_PATH, "my.cnf")

        if not os.path.exists(backup_file):
            return True, "Can not find backup file:{}".format(backup_file)

        with open(backup_file, "r", encoding="UTF-8") as f:
            backup_content = f.read()

        with open(self.mycnf, "w") as f:
            f.write(backup_content)

        backup_time = time.asctime(time.localtime(os.path.getctime(backup_file)))
        os.remove(backup_file)
        return True, backup_time

    @functionLog
    def backup(self, param_list: dict):
        backup_content = ""
        backup_file = os.path.join(Config.BACNUP_PATH, "my.cnf")
        if os.path.exists(backup_file):
            suc, result = self.rollback()
            if not suc:
                return False, "backup file exists, rollback to last backup point failed:{}".format(result)

        with open(self.mycnf, "r", encoding="UTF-8") as f:
            backup_content = f.read()

        with open(backup_file, "w") as f:
            f.write(backup_content)

        return True, backup_file
