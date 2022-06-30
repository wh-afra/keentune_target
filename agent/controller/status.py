import json

from tornado.web import RequestHandler
from agent.domain import DOMAINOBJ

class StatusHandler(RequestHandler):
    """ Alive check.

    """
    def get(self):
        back_json = {"status": "alive"}
        self.write(json.dumps(back_json))
        self.finish()


class AvaliableDomainHandler(RequestHandler):
    """ Get avaliable domain list

    """
    def get(self):
        avaliable_domain = list(DOMAINOBJ.keys())
        self.write(json.dumps({"result":avaliable_domain}))
        self.finish()