import json

from tornado.web import RequestHandler
from target.common.pylog import APILog
from target.controller import DomainObj


class BackupHandler(RequestHandler):
    def _backImpl(self, param_domain_dict:dict):
        """ Call the backup() function of each parameter domain in turn
        """
        domain_result = {}
        SUCCESS = True
        for domain in param_domain_dict.keys():
            param_list = param_domain_dict[domain]
            suc, out = DomainObj[domain].backup(param_list)

            SUCCESS = SUCCESS and suc
            domain_result[domain] = out
        return SUCCESS, domain_result

    def _validDomain(self,param_domain_dict):
        """ Check the legality of all domain defined in param_domain_dict
        """
        for domain in param_domain_dict.keys():
            if not DomainObj.__contains__(domain):
                raise Exception("Unsupported parameter domain '{}'".format(domain))

    @APILog
    def post(self):
        """ Backup parameters value to backup file
        """
        param_domain_dict = json.loads(self.request.body)
        try:
            self._validDomain(param_domain_dict)
        
        except Exception as e:
            self.write(json.dumps({"suc" : False,"msg" : str(e)}))
            self.finish()

        else:
            suc, domain_result = self._backImpl(param_domain_dict)
            self.write(json.dumps({"suc":suc, "msg":domain_result}))
            self.finish()
