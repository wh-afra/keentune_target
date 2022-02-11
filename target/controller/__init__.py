import os  
import re

from importlib import import_module

from target import domain
from target.common import pylog

DomainObj = {}

def _getSubmodule(package):
    submodules = [re.sub('.py','',f) for f in os.listdir(package.__path__[0]) if not re.search('__',f)]
    return submodules

def loadParameterDomain():
    """ Load all parameter domain in directory 'target/domain'
    """
    global DomainObj
    domain_list = _getSubmodule(domain)

    DomainObj = {}
    for domain_name in domain_list:
        try:
            module = import_module('target.domain.{}'.format(domain_name))
            domain_obj = eval('domain.{domain_name}.{class_name}()'.format(
                domain_name = domain_name,
                class_name  = domain_name.capitalize()
            ))

        except Exception as e:
            pylog.logger.error("Failed to import domain '{}': {}".format(domain_name,e))
            print("[-] Failed to import domain '{}': {}".format(domain_name,e))

        else:
            pylog.logger.info("[+] Load parameter domain '{}' ({})".format(domain_name, module))
            print("[+] Load parameter domain '{}' ({})".format(domain_name, module))
            DomainObj[domain_name] = domain_obj

loadParameterDomain()