import json

from tornado.web import RequestHandler
from target.common.pylog import APILog
from target.common.system import sysCommand


class DetectHandler(RequestHandler):
    @APILog
    def post(self):
        """ Detect parameters value
        """
        request_data = json.loads(self.request.body)

        response_data = {}
        for param_name, command in request_data["data"].items():
            suc, res = sysCommand(command)
            if not suc:
                result = {
                    "suc": False,
                    "value": 0,
                    "msg": res
                    }
            else:
                result = {
                    "suc": True,
                    "value": int(res),
                    "msg": ""
                }
            response_data[param_name] = result
        self.write(json.dumps(response_data))
        self.finish()