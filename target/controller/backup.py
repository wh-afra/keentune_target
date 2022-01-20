import json

from tornado.web import RequestHandler

from target import scene
from target.common.pylog import APILog


class BackupHandler(RequestHandler):
    @APILog
    def post(self):
        """ Backup parameters value to backup file
        """
        param_domain_dict = json.loads(self.request.body)

        suc, res = scene.ACTIVE_SCENE.backup(param_domain_dict)

        response_data = {
            "suc": suc,
            "msg": res
        }
        self.write(json.dumps(response_data))
        self.finish()
