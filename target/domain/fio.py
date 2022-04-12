import os
import re

from target.common.config import Config
from target.common.pylog import functionLog


class Fio:
    def __init__(self):
        pass

    @functionLog
    def _beforeParamSet(self):
        return True, "unnecessary"

    @functionLog
    def _afterParamSet(self):
        return True, "unnecessary"

    @functionLog
    def setParamAll(self, param_list):
        command = "fio -ioengine=psync -time_based=1 -rw=read"
        result = {}
        for param_name, param_info in param_list.items():
            command += " -{} {}".format(param_name[0], param_info["value"])
            result[param_name] = {
                "value": param_info["value"],
                "dtype": param_info["dtype"],
                "suc": True,
                "msg": ""
            }

        path = os.path.join(Config.keentune_workspace, "files", "benchmark/fio/ack_fio_IOPS_base.py")
        with open(path, "r", encoding='UTF-8') as f:
            data = f.read()
            data = re.sub(r"SIZE = \d+", "SIZE = {}".format(param_list["size"]["value"]), data)
            data = re.sub(r"NumJobs = \d+", "NumJobs = {}".format(param_list["numjobs"]["value"]), data)
            data = re.sub(r'COMMAND = "[a-zA-Z\d\-\s]+"', 'COMMAND = "{}"'.format(command), data)
        with open(path, "w", encoding='UTF-8') as f:
            f.write(data)

        return True, result

    @functionLog
    def getParamAll(self, param_list):
        param_dict = {
            "size": 110,
            "bs": "512B",
            "numjobs": 1
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
        return True, "fio don't need rollback!"

    @functionLog
    def backup(self, _):
        return True, "fio don't need backup!"
