from xmlrpc.client import FastParser
from agent.common.system import sysCommand, getNUMA, getActiveNetCard
from collections import defaultdict

from agent.common.pylog import logger

NET_CARD_NUM = 8    # TODO: Read network card number from environment

XPS_SET = "echo {} > /sys/class/net/eth0/queues/rx-{}/xps_cpus"
RPS_SET = "echo {} > /sys/class/net/eth0/queues/tx-{}/rps_cpus"

XPS_SCHEME = {
    '0': ['00','00','00','00','00','00','00','00'],
    '1': ['01','04','10','40','02','08','20','80']
}

RPS_SCHEME = {
    '0': ['00','00','00','00','00','00','00','00'],
    '1': ['01','04','10','40','02','08','20','80']
}

SMP_AFFINITY_SET = "echo {core_id} > /proc/irq/{queue_id}/smp_affinity_list"

class Net:
    def __init__(self) -> None:
        super().__init__()

    def setParamAll(self, param_list: dict):
        def _scheme_set(value, SET_CMD, SCHEME_LIST):
            if not value in SCHEME_LIST.keys():
                logger.error("unsupported value {} of knos xps".format(value))
                return False, "unsupported value {} of knos xps".format(value)
            
            _scheme = SCHEME_LIST[value]
            if _scheme.__len__() > NET_CARD_NUM:
                logger.error("numbers of network card {} is too small".format(NET_CARD_NUM))
                return False, "numbers of network card {} is too small".format(NET_CARD_NUM)
            
            for i in range(_scheme.__len__()):
                suc, res = sysCommand(SET_CMD.format(
                    _scheme[i],
                    i
                ))
                if not suc:
                    logger.error(res)
                    return False, res
            return True, ""


        def _smp_affinity_set(value):
            dev_name, bus_info, network_queue= getActiveNetCard()
            numa_node_core_range = getNUMA(bus_info)
            logger.info("smp_affinity set, dev:{}   \
                        mode:{}   \
                        network queue:{}   \
                        numa_node_core:{}~{}".format(
                        dev_name, value, network_queue, numa_node_core_range[0],numa_node_core_range[1]))

            if value == "dedicated":
                # shutdown the irqbalance service
                suc, res = sysCommand("systemctl stop irqbalance.service")
                if not suc:
                    return False, "Failed to shutdown irqbalance.service"
                
                # moving interrupts to a dedicated CPU
                logger.info("moving interrupts to a dedicated CPU: {}".format(numa_node_core_range[0]))
                for queue_id in network_queue:
                    suc, res = sysCommand(SMP_AFFINITY_SET.format(
                        core_id  = numa_node_core_range[0],
                        queue_id = queue_id
                    ))
                    if not suc:
                        return False, res
                return True, ""
                
            if value == "different":
                suc, res = sysCommand("systemctl stop irqbalance.service")
                if not suc:
                    return False, "Failed to shutdown irqbalance.service"
                
                # moving interrupts to different CPUs
                logger.info("moving interrupts to a different CPUs: {}~{}".format(
                    numa_node_core_range[0],numa_node_core_range[1]))
                
                for index, queue_id in enumerate(network_queue):
                    suc, res = sysCommand(SMP_AFFINITY_SET.format(
                        core_id  = numa_node_core_range[0] + index%(
                                    numa_node_core_range[1]-numa_node_core_range[0]),
                        queue_id = queue_id
                    ))
                    if not suc:
                        return False, res
                return True, ""

            if value == "off":
                suc, res = sysCommand("systemctl restart irqbalance.service")
                for index, queue_id in enumerate(network_queue):
                    suc, res = sysCommand(SMP_AFFINITY_SET.format(
                        core_id  = "{}-{}".format(numa_node_core_range[0], numa_node_core_range[1]),
                        queue_id = queue_id
                    ))
                    if not suc:
                        return False, res
                return True, ""


        result = defaultdict(dict)
        success = False
        for param_name, param_info in param_list.items():
            if param_name.lower() == "xps":
                _suc, _res = _scheme_set(param_info['value'], XPS_SET, XPS_SCHEME)
                
            elif param_name.lower() == "rps":
                _suc, _res = _scheme_set(param_info['value'], RPS_SET, RPS_SCHEME)

            elif param_name.lower() == "smp_affinity":
                _suc, _res = _smp_affinity_set(param_info['value'])
            else:
                logger.warning("unknown parameters {}".format(param_name))
                _suc, _res = False, "unknown parameters {}".format(param_name)

            success = success | _suc
            result[param_name] = {
                "value" : param_info['value'],
                "dtype" : param_info["dtype"],
                "suc"   : _suc,
                "msg"   : _res
            }

        return success,result

if __name__ == "__main__":
    net = Net()
    net.setParamAll({
        "smp_affinity": {
            'value':'different',
            'dtype':'int'
        }
    })