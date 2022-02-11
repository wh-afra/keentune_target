import json

from tornado.web import RequestHandler
from target.common.system import HTTPPost
from target.controller import DomainObj


class ConfigureHandler(RequestHandler):
    def _configureImpl(self, param_domain_dict:dict, readonly:bool):
        """ Call getParamAll() function or setParamAll() function of each parameter domain in turn
        """
        domain_result = {}
        SUCCESS = True
        for domain in param_domain_dict.keys():
            param_list = param_domain_dict[domain]
            if readonly:
                suc, out = DomainObj[domain].getParamAll(param_list)
            else:
                suc, out = DomainObj[domain].setParamAll(param_list)
            SUCCESS = SUCCESS and suc
            domain_result[domain] = out

        return SUCCESS, domain_result


    def _validDomain(self,param_domain_dict):
        """ Check the legality of all domain defined in param_domain_dict
        """
        for domain in param_domain_dict.keys():
            if not DomainObj.__contains__(domain):
                raise Exception("Unsupported parameter domain '{}'".format(domain))


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
            self._validDomain(param_domain_dict)

        except KeyError as error_key:
            self.write(json.dumps({
                "suc" : False,
                "msg" : "Interface call error: can not find key: {}".format(error_key)
            }))
            self.finish()
            return

        except Exception as e:
            self.write(json.dumps({"suc" : False, "msg": str(e)}))
            self.finish()
            return

        else:
            self.write(json.dumps({"suc" : True, "msg" : ""}))
            self.finish()

        suc, out = self._configureImpl(param_domain_dict, readonly)
        if suc:
            response = {"suc": True, "data": out, "target_id": target_id, "msg": ""}
        else:
            response = {"suc": False, "data": {}, "target_id": target_id, "msg": out}

        await HTTPPost(
            api  = "apply_result",
            ip   = resp_ip,
            port = resp_port,
            data = response
        )