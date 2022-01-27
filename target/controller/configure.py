import json

from tornado.web import RequestHandler
from target import scene
from target.common.system import HTTPPost


class ConfigureHandler(RequestHandler):
    # @APILog
    async def post(self):
        """ Getting and setting parameter values

        Setting parameter value if parameter value is not None.
        Getting all parameter value defined in resquest data.

        """
        request_data = json.loads(self.request.body)

        try:
            readonly    = request_data['readonly']
            resp_ip     = request_data['resp_ip']
            resp_port   = request_data['resp_port']
            target_id   = request_data['target_id']
            param_domain_dict = request_data['data']

        except KeyError as error_key:
            self.write(json.dumps({
                "suc" : False,
                "msg" : "Interface call error: can not find key: {}".format(error_key)
            }))
            self.finish()

        else:
            self.write(json.dumps({
                "suc" : True,
                "msg" : ""
            }))
            self.finish()

            if readonly:
                suc, res = scene.ACTIVE_SCENE.paramGet(param_domain_dict)
            else:
                suc, res = scene.ACTIVE_SCENE.paramSet(param_domain_dict)
            
            if suc:
                response_data = {
                    "suc": True, "data": res, "target_id": target_id, "msg": ""}
            else:
                response_data = {
                    "suc": False, "data": {}, "target_id": target_id, "msg": res}

            suc, res = await HTTPPost(
                api="apply_result",
                ip=resp_ip,
                port=resp_port,
                data=response_data
            )
