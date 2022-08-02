import os
import time

from agent.common.config import Config
from agent.common.system import sysCommand
from collections import defaultdict

from agent.common.pylog import logger

HUGEPAGE_GET = "cat /sys/kernel/mm/transparent_hugepage/hugetext_enabled"
HUGEPAGE_SET = "echo {value} > /sys/kernel/mm/transparent_hugepage/hugetext_enabled"
HUGEPAGE_CLEAR = "echo 1 > /sys/kernel/debug/split_huge_pages"
HUGEPAGE_CLEAR_PAGE_CACHE = "echo 3 > /proc/sys/vm/drop_caches"

class Hugepage:
    def __init__(self):
        super().__init__()
        self.backup_file = os.path.join(Config.BACNUP_PATH, "hugepage_backup.txt")

    def _code_hugepage_set(self, value):
        _value = int(value)
        if _value == 0:
            logger.info("clear huge page.")
            _suc, _res = sysCommand(HUGEPAGE_CLEAR)
            if not _suc:
                return False, _res
            logger.info("clear page cache.")
            _suc, _res = sysCommand(HUGEPAGE_CLEAR_PAGE_CACHE)
            if not _suc:
                return False, _res
        return sysCommand(HUGEPAGE_SET.format(value = _value))


    def setParamAll(self, param_list: dict):
        result = defaultdict(dict)
        success = False
        for param_name, param_info in param_list.items():
            if param_name.lower() == "code_hugepage":
                _suc, _res = self._code_hugepage_set(param_info['value'])
                result[param_name] = {
                    "value" : param_info['value'],
                    "dtype" : param_info["dtype"],
                    "suc"   : _suc,
                    "msg"   : _res
                }
            success = success | _suc
        return success, result
    

    def getParamAll(self, param_list: dict):
        result = defaultdict(dict)
        for param_name, param_info in param_list.items():
            result[param_name] = {
                "value" : "",
                "dtype" : param_info["dtype"],
                "suc"   : True,
                "msg"   : "This domain is not supported to parameter value reading."
            }
        return True, result

    def rollback(self):
        if not os.path.exists(self.backup_file):
            return True, "Can not find backup file:{}".format(self.backup_file)

        with open(self.backup_file, 'r') as f:
            value = f.read().strip("\n")

        suc, res = self._code_hugepage_set(value)
        if suc:
            backup_time = time.asctime(time.localtime(os.path.getctime(self.backup_file)))
            logger.info("Rollback to backup time: {}".format(backup_time))
            os.remove(self.backup_file)
            return True, backup_time
        else:
            logger.error("Failed to rollback: {}".format(res))
            return False, res

    def backup(self, param_list: dict):
        if os.path.exists(self.backup_file):
            suc, res = self.rollback()
            if not suc:
                return False, res

        suc, res = sysCommand(HUGEPAGE_GET)
        if suc:
            with open(self.backup_file, 'w') as f:
                f.write(res)
            return True, self.backup_file
        if not suc:
            return False, "backup hugepage conf failed: {}".format(res)


if __name__ == "__main__":
    hugepage = Hugepage()
    print(hugepage.setParamAll({"code_hugepage": {'value':'0','dtype':'str'}}))
    print(hugepage.setParamAll({"code_hugepage": {'value':'1','dtype':'str'}}))
    print(hugepage.setParamAll({"code_hugepage": {'value':'2','dtype':'str'}}))
    print(hugepage.setParamAll({"code_hugepage": {'value':'3','dtype':'str'}}))
    print(hugepage.setParamAll({"code_hugepage": {'value':'0','dtype':'str'}}))