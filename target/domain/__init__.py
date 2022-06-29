import os
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
        raise e

    else:
        pylog.logger.info("Load parameter domain '{}' ({})".format(domain_name, module))
        DOMAINOBJ[domain_name] = domain_obj


def loadSupportedDoamin():
    """ try to load all avaliable domain in folder /target/domain

    """
    domain_list = [i.split(".")[0] for i in os.listdir(os.path.split(os.path.abspath(__file__))[0]) 
        if i != os.path.split(os.path.abspath(__file__))[1] and not os.path.isdir(os.path.join(os.path.split(os.path.abspath(__file__))[0], i))]

    pylog.logger.info("Parseing and trying to load domains defined in {}".format(
        os.path.split(os.path.abspath(__file__))[0]
    ))

    for domain_name in domain_list:
        try:
            loadDoamin(domain_name)
        except Exception as e:
            continue