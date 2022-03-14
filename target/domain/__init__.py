from importlib import import_module

from target import domain
from target.common import pylog

DOMAINOBJ = {}

def loadDoamin(domain_name):
    global DOMAINOBJ
    if DOMAINOBJ.__contains__(domain_name):
        return 
    
    try:
        module = import_module('target.domain.{}'.format(domain_name))
        domain_obj = eval('domain.{domain_name}.{class_name}()'.format(
            domain_name = domain_name,
            class_name = "".join([value.capitalize() for value in domain_name.split("_")]) if "_" in domain_name else domain_name.capitalize()
        ))

    except Exception as e:
        pylog.logger.warning("parameter domain {} is not supported by current environment: {}".format(domain_name,e))
        print("[warning] domain {} is not supported by current environment:{}".format(domain_name,e))
        raise e

    else:
        pylog.logger.info("Load parameter domain '{}' ({})".format(domain_name, module))
        print("[+] Load parameter domain '{}'".format(domain_name))
        DOMAINOBJ[domain_name] = domain_obj