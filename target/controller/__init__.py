import re  
import os  

from importlib import import_module

from target import domain
from target.common import pylog

DOMAINOBJ = {}

def _getSubmodule(package):
    submodules = [re.sub('.py','',f) for f in os.listdir(package.__path__[0]) if not re.search('__',f)]
    return submodules


def _loadDoamin(domain_name):
    global DOMAINOBJ

    try:
        module = import_module('target.domain.{}'.format(domain_name))
        domain_obj = eval('domain.{domain_name}.{class_name}()'.format(
            domain_name = domain_name,
            class_name = "".join([value.capitalize() for value in domain_name.split("_")]) if "_" in domain_name else domain_name.capitalize()
        ))

    except Exception as e:
        pylog.logger.warning("parameter domain {} is not supported by current environment: {}".format(domain_name,e))
        print("[warning] domain {} is not supported by current environment:{}".format(domain_name,e))

    else:
        pylog.logger.info("Load parameter domain '{}' ({})".format(domain_name, module))
        print("[+] Load parameter domain '{}'".format(domain_name))
        DOMAINOBJ[domain_name] = domain_obj


def loadAllDomain():
    domain_list = _getSubmodule(domain)
    for domain_name in domain_list:
        _loadDoamin(domain_name)


loadAllDomain()