import json

from tornado.web import RequestHandler
from target.common.pylog import APILog
from target.controller import DomainObj


class RollbackHandler(RequestHandler):
    def _rollbackImpl(self):
        """ Call rollback() function of each parameter domain in turn
        """
        domain_result = {}
        SUCCESS = True
        for domain in DomainObj.keys():
            suc, out = DomainObj[domain].rollback()
            SUCCESS = SUCCESS and suc
            domain_result[domain] = out
        return SUCCESS, domain_result

    @APILog
    def post(self):
        _ = json.loads(self.request.body)
        suc, out = self._rollbackImpl()
        self.write(json.dumps({
            "suc": suc,
            "msg": out
        }))
        self.finish()