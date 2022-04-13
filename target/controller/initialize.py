import os
import re
import json
import subprocess
from target import domain
from importlib import import_module
from tornado.web import RequestHandler


class InitializeHandler(RequestHandler):
    def post(self):
        rollbackfun=target.common.initialize.RollbackAll()
        suc, out = rollbackfun.all()

        self.write(json.dumps({"suc": suc,"msg": out}))
        self.finish()


backup_dir="/var/keentune/ServiceBackup"
config=("sysctl", "nginx")

def backupall():
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)
    elif not os.path.isdir(backup_dir):
        os.remove(backup_dir)
        os.mkdir(backup_dir)

    submodules = [re.sub('.py','',f) for f in os.listdir(domain.__path__[0]) if not re.search('__',f)]
    for domain_name in submodules:
        if domain_name in config:
            moudle = import_module("target.domain.{}".format(domain_name))
            suc, res = moudle.initialize()
            if suc:
                print("[+]{}: {}".format(domain_name,res))
            else:
                print("[-]warning {}: {}".format(domain_name,res))
