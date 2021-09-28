import os
import json
import time

from target.common.config import Config
from target.common.system import sysCommand
from target.common.pylog import functionLog


class Sysctl:
    name = "sysctl"
    get_cmd = "sysctl -n {name}"
    set_cmd = "sysctl -w {name}='{value}'"
    backup_file = os.path.join(
        Config.backup_dir, "{}_backup.json".format(name))

    def __init__(self):
        super().__init__()

    @functionLog
    def _setParam(self, param_name: str, param_info: dict):
        set_cmd = self.set_cmd.format(
            name=param_name.strip(),
            value=param_info['value'])

        return sysCommand(
            command=set_cmd,
            cwd=Config.keentune_script_dir)

    @functionLog
    def _getParam(self, param_name: str, param_info: dict):
        get_cmd = self.get_cmd.format(name=param_name.strip())

        return sysCommand(
            command=get_cmd,
            cwd=Config.keentune_script_dir)

    @functionLog
    def _beforeParamSet(self):
        return True, "unnecessary"

    @functionLog
    def _afterParamSet(self):
        return True, "unnecessary"

    @functionLog
    def setParamAll(self, param_list: dict):
        suc, res = self._beforeParamSet()
        if not suc:
            return False, res

        result = {}
        for param_name, param_info in param_list.items():
            if param_info['value'] == "":
                continue

            suc, res = self._setParam(param_name, param_info)
            result[param_name] = {
                "value": param_info["value"],
                "dtype": param_info["dtype"],
                "suc": suc,
                "msg": res
            }

        suc, res = self._afterParamSet()
        if not suc:
            return False, res

        return True, result

    @functionLog
    def getParamAll(self, param_list: dict):
        result = {}
        for param_name, param_info in param_list.items():
            suc, res = self._getParam(param_name, param_info)

            result[param_name] = {
                "value": param_info["value"],
                "dtype": param_info["dtype"],
                "suc": suc,
                "msg": res
            }
        return True, result

    @functionLog
    def rollback(self):
        if not os.path.exists(self.backup_file):
            return True, "Can not find backup file:{}".format(self.backup_file)

        with open(self.backup_file, "r") as f:
            backup_content = json.load(f)

            for param_name, param_value in backup_content.items():
                set_cmd = param_value["set_cmd"].format(
                    name=param_name,
                    value=param_value["value"])

                suc, result = sysCommand(
                    command=set_cmd,
                    cwd=Config.keentune_script_dir)

                if not suc:
                    return False, "rollback parameter {} to {} failed:{}".format(
                        param_name, param_value, result)

        backup_time = time.asctime(time.localtime(
            os.path.getctime(self.backup_file)))
        os.remove(self.backup_file)
        return True, backup_time

    @functionLog
    def backup(self, param_list: dict):
        if os.path.exists(self.backup_file):
            suc, res = self.rollback()
            if not suc:
                return False, res

        backup_content = {}
        for param_name, param_info in param_list.items():
            suc, param_value = self._getParam(param_name, param_info)
            if not suc:
                return False, param_value

            values = {
                "get_cmd": self.get_cmd,
                "set_cmd": self.set_cmd,
                "value": param_value
            }

            backup_content[param_name] = values

        with open(self.backup_file, "w") as f:
            f.write(json.dumps(backup_content))

        return True, self.backup_file
