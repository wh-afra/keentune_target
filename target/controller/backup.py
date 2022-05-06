import json

from tornado.web import RequestHandler

from target.domain import DOMAINOBJ, loadDoamin


class BackupHandler(RequestHandler):
    def _backImpl(self, param_domain_dict:dict):
        """ Call the backup() function of each parameter domain in turn
        """
        domain_result = {}
        SUCCESS = True
        for domain in param_domain_dict.keys():
            param_list = param_domain_dict[domain]
            suc, out = DOMAINOBJ[domain].backup(param_list)

            SUCCESS = SUCCESS and suc
            domain_result[domain] = out
        return SUCCESS, domain_result

    def post(self):
        """ Backup parameters value to backup file
        """
        def _validDomain(param_domain_dict):
            """ Check the legality of all domain defined in param_domain_dict
            """
            for domain in param_domain_dict.keys():
                loadDoamin(domain)

        param_domain_dict = json.loads(self.request.body)
        try:
            _validDomain(param_domain_dict)

        except Exception as e:
            self.write(json.dumps({"suc" : False,"msg" : str(e)}))
            self.finish()

        else:
            suc, domain_result = self._backImpl(param_domain_dict)
            self.write(json.dumps({"suc":suc, "msg":domain_result}))
            self.finish()