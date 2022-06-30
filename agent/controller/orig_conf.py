import os
import json
from tornado.web import RequestHandler

from agent.domain import DOMAINOBJ, loadSupportedDoamin
from agent.common import pylog
from agent.common.config import Config

class OriginalConfigurationHandler(RequestHandler):
    def post(self):
        suc, out = _rollbackOriginalConfiguration()
        self.write(json.dumps({"suc": suc,"msg": out}))
        self.finish()


def backupOriginalConfiguration():
    loadSupportedDoamin()
    if not os.path.exists(Config.ORIGINAL_CONF_PATH):
        os.mkdir(Config.ORIGINAL_CONF_PATH)
    
    for domain_name in DOMAINOBJ.keys():
        try:
            suc, res = DOMAINOBJ[domain_name].originalConfig("backup")
        except AttributeError as e:
            continue
        if suc:
            pylog.logger.info("Backup original configuration of domain {}".format(domain_name))
        else:
            print("[-]warning {}: {}".format(domain_name,res))


def _rollbackOriginalConfiguration():
    result = {}
    success = True
    for domain_name in DOMAINOBJ.keys():
        try:
            suc, res = DOMAINOBJ[domain_name].originalConfig("rollback")
        except AttributeError as e:
            continue
        if suc:
            pylog.logger.info("Success to rollback to original configuration of domain {}".format(domain_name))
            result[domain_name] = {"suc": True, "msg": res}
        else:
            pylog.logger.error("Fail to rollback domain {}: {}".format(domain_name, res))
            success = False
            result[domain_name] = {"suc": False, "msg": res}
    return success, result