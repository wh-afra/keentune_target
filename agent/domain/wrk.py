import json
import os
import re

from agent.common.config import Config
from agent.common.pylog import functionLog


class Wrk:
    def __init__(self):
        super().__init__()

    @functionLog
    def _beforeParamSet(self):
        return True, "unnecessary"

    @functionLog
    def _afterParamSet(self):
        return True, "unnecessary"

    @functionLog
    def setParamAll(self, param_list: dict):
        command = ""
        result = {}
        for param_name, param_info in param_list.items():
            command += "--{} {} ".format(param_name, param_info["value"])
            result[param_name] = {
            "value": param_info["value"],
            "dtype": param_info["dtype"],
            "suc": True,
            "msg": ""
        }

        path = os.path.join(Config.FILES_PATH, "benchmark/wrk/wrk_parameter_tuning.py")
        with open(path, "r", encoding='UTF-8') as f:
            data = f.read()
            data = re.sub(r'DEFAULT = "[a-zA-Z0-9\-=\s]*"', 'DEFAULT = "{}"'.format(command), data)
        with open(path, "w", encoding='UTF-8') as f:
            f.write(data)

        return True, result

    @functionLog
    def getParamAll(self, param_list: dict):
        param_dict = {
            "connections": 10,
            "threads": 2,
        }

        param_res_info = {}
        print(param_list)
        for param_name, param_info in param_list.items():
            param_res_info[param_name] = {
                "value": param_dict[param_name],
                "dtype": param_info["dtype"],
                "suc": True,
                "msg": ""}

        return True, param_res_info

    @functionLog
    def rollback(self):
        return True, "wrk don't need rollback!"

    @functionLog
    def backup(self, param_list: dict):
        return True, "wrk don't need backup!"

