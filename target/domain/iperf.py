import os
import re

from target.common.config import Config
from target.common.pylog import functionLog


class Iperf:
    @functionLog
    def _beforeParamSet(self):
        return True, "unnecessary"

    @functionLog
    def _afterParamSet(self):
        return True, "unnecessary"

    @functionLog
    def setParamAll(self, param_list):
        command = "-t 15 -M 1500"
        result = {}
        for param_name, param_info in param_list.items():
            command += " -{} {}".format(param_name[0], param_info["value"])
            result[param_name] = {
                "value": param_info["value"],
                "dtype": param_info["dtype"],
                "suc": True,
                "msg": ""
            }

        path = os.path.join(Config.keentune_workspace, "files", "benchmark/iperf/iperf.py")
        with open(path, "r", encoding='UTF-8') as f:
            data = f.read()
            data = re.sub(r"PARALLEL_DATA = \d+", "PARALLEL_DATA = {}".format(param_list["Parallel"]["value"]), data)
            data = re.sub(r'COMMAND = "[a-zA-Z\d\-\s]+"', 'COMMAND = "{}"'.format(command), data)
        with open(path, "w", encoding='UTF-8') as f:
            f.write(data)

        return True, result

    @functionLog
    def getParamAll(self, param_list):
        param_dict = {
            "Parallel": 1,
            "window_size": 10240,
            "length_buffers": 10240
        }
        result = {}
        for param_name, param_info in param_list.items():
            result[param_name] = {
                "value": param_dict[param_name], 
                "dtype": param_info["dtype"], 
                "suc": True, 
                "msg": ""
            }

        return True, result

    @functionLog
    def rollback(self):
        return True, "iperf don't need rollback!"

    @functionLog
    def backup(self):
        return True, "iperf don't need backup!"