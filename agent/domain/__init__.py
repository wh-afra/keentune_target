from importlib import import_module

from agent import domain
from agent.common import pylog

DOMAINOBJ = {}
ALL_DOMAIN_LIST = ['sysctl', 'nginx', 'iperf', 'sysbench', 'net', 'hugepage', 'mycnf']

def loadDoamin(domain_name):
    global DOMAINOBJ
    if DOMAINOBJ.__contains__(domain_name):
        return
    
    try:
        module = import_module('agent.domain.{}'.format(domain_name))
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
    """ try to load all avaliable domain in folder /agent/domain

    """
    for domain_name in ALL_DOMAIN_LIST:
        try:
            loadDoamin(domain_name)
        except Exception as e:
            continue