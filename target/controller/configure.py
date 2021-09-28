import json

from tornado.web import RequestHandler

from target import scene
from target.common.config import Config
from target.common.pylog import functionLog, APILog
from target.common.system import HTTPPost
from target.common import pylog


class ConfigureHandler(RequestHandler):
    # @APILog
    async def post(self):
        """ Getting and setting parameter values

        Setting parameter value if parameter value is not None.
        Getting all parameter value defined in resquest data.

        """
        request_data = json.loads(self.request.body)

        try:
            resp_ip = request_data['resp_ip']
            resp_port = request_data['resp_port']
            param_domain_dict = request_data['data']

        except KeyError as error_key:
            self.write(json.dumps({
                "suc": False,
                "msg": "can not find key: {}".format(error_key)

            }))
            self.finish()

        else:
            self.write(json.dumps({
                "suc": True,
                "msg": ""

            }))
            self.finish()

            suc, res = scene.ACTIVE_SCENE.paramSet(param_domain_dict)
            if suc:
                response_data = {
                    "suc": True, "data": res, "msg": ""}
            else:
                response_data = {
                    "suc": False, "data": {}, "msg": res}

            suc, res = await HTTPPost(
                api="apply_result",
                ip=resp_ip,
                port=resp_port,
                data=response_data
            )
