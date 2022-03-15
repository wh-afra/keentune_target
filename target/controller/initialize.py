import json

from tornado.web import RequestHandler
import target.common.initialize

class InitializeHandler(RequestHandler):
    def post(self):
        rollbackfun=target.common.initialize.RollbackAll()
        suc, out = rollbackfun.all()

        self.write(json.dumps({"suc": suc,"msg": out}))
        self.finish()

