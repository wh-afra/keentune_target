import json

from tornado.web import RequestHandler

from target import scene
from target.common.pylog import APILog


class RollbackHandler(RequestHandler):
    @APILog
    def post(self):
        """Handle rollback request

        Request data format:
            request_data = {
                "type": tune type. e.g. 'vm'
            } 

        Resonse data format:
            response_data = {
                "suc": if operation success.
                "msg": error message or empty string.
            }
        """
        request_data = json.loads(self.request.body)

        suc, res = scene.ACTIVE_SCENE.rollback()

        if suc:
            response_data = {
                "suc": True,
                "msg": "rollback successfully:{}".format(res)
            }
        else:
            response_data = {
                "suc": False,
                "msg": res
            }

        self.write(json.dumps(response_data))
        self.finish()
