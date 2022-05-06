import json

from tornado.web import RequestHandler


class StatusHandler(RequestHandler):
    def get(self):
        back_json = {"status": "alive"}
        self.write(json.dumps(back_json))
        self.finish()
