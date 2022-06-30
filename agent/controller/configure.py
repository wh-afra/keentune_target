import json
import traceback

from tornado.web import RequestHandler
from agent.domain import DOMAINOBJ, loadDoamin
from agent.common import pylog

from tornado.httpclient import HTTPClient, HTTPRequest, HTTPError
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado.gen import coroutine

class ConfigureHandler(RequestHandler):
    executor = ThreadPoolExecutor(20)

    @run_on_executor
    def _response(self,
                  response_data:dict,
                  response_ip  :str,
                  response_port:str):
        http_client = HTTPClient()
        try:
            URL = "http://{ip}:{port}/apply_result".format(
                            ip = response_ip, port = response_port)
            pylog.logger.info("response to {}".format(URL))

            response = http_client.fetch(HTTPRequest(
                url    =  URL,
                method = "POST",
                body   = json.dumps(response_data)
            ))
        except RuntimeError as e:
            pylog.logger.error("Failed to response to {}: {}".format(URL, e))
            return False, "{},{}".format(e, traceback.format_exc())

        except HTTPError as e:
            pylog.logger.error("Failed to response to {}: {}".format(URL, e))
            return False, "{},{}".format(e, traceback.format_exc())

        except Exception as e:
            pylog.logger.error("Failed to response to {}: {}".format(URL, e))
            return False, "{},{}".format(e, traceback.format_exc())

        else:
            if response.code == 200:
                return True, ""
            else:
                return False, response.reason

        finally:
            http_client.close()


    @run_on_executor
    def _configureImpl(self, param_domain_dict:dict, readonly:bool):
        """ Call getParamAll() function or setParamAll() function of each parameter domain in turn
        """
        global DOMAINOBJ
        domain_result = {}
        SUCCESS = False
        for domain in param_domain_dict.keys():
            param_list = param_domain_dict[domain]
            if readonly:
                suc, out = DOMAINOBJ[domain].getParamAll(param_list)
            else:
                suc, out = DOMAINOBJ[domain].setParamAll(param_list)
            SUCCESS = SUCCESS or suc
            domain_result[domain] = out
        return SUCCESS, domain_result


    @coroutine
    def post(self):
        global DOMAINOBJ
        def _validDomain(param_domain_dict):
            """ Check the legality of all domain defined in param_domain_dict
            """

            for domain in param_domain_dict.keys():
                loadDoamin(domain)

        def _validField(request_data):
            assert request_data.__contains__('readonly')
            assert request_data.__contains__('resp_ip')
            assert request_data.__contains__('resp_port')
            assert request_data.__contains__('target_id')
            assert request_data.__contains__('data')

        request_data = json.loads(self.request.body)
        pylog.logger.info("get configure request: {}".format(request_data))

        try:
            _validField(request_data)
            _validDomain(request_data['data'])

        except Exception as e:
            pylog.logger.error("Failed to response request: {}".format(e))
            self.write(json.dumps({"suc" : False, "msg": str(e)}))
            self.finish()
            
        else:
            self.write(json.dumps({"suc" : True, "msg" : "parameter set/get is running"}))
            self.finish()

            suc, out = yield self._configureImpl(request_data['data'], request_data['readonly'])
            if suc:
                response_data = {
                    "suc"       : True, 
                    "data"      : out, 
                    "target_id" : request_data['target_id'], 
                    "msg"       : ""
                }
            else:     
                response_data = {
                    "suc"       : False, 
                    "data"      : {}, 
                    "target_id" : request_data['target_id'], 
                    "msg"       : out
                }   
            _, _ = yield self._response(response_data, request_data['resp_ip'], request_data['resp_port'])