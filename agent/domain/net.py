import os
import time

from agent.common.config import Config
from agent.common.system import sysCommand
from agent.common.system import getNUMA, getActiveNetCard, getCPUInfo
from collections import defaultdict

from agent.common.pylog import logger

XPS_SET = "echo {core_code} > /sys/class/net/{dev_name}/queues/{queue_id}/xps_cpus"
XPS_GET = "cat /sys/class/net/{dev_name}/queues/{queue_id}/xps_cpus"

RPS_SET = "echo {core_code} > /sys/class/net/{dev_name}/queues/{queue_id}/rps_cpus"
RPS_GET = "cat /sys/class/net/{dev_name}/queues/{queue_id}/rps_cpus"

SMP_AFFINITY_SET = "echo {core_id} > /proc/irq/{queue_id}/smp_affinity_list"
SMP_AFFINITY_GET = "cat /proc/irq/{queue_id}/smp_affinity_list"

class Net:
    def __init__(self):
        """ init net device setting domain

        1. Read network card information, i.e. dev name, bus_info, interrupts queue, xps/rps queue.
        2. Read NUMA node range for interrupts setting.
        3. Read CPU core number for xps/rps setting.
        """
        super().__init__()
        self.dev_name, \
        self.bus_info, \
        self.interrupts_queue, \
        self.rx_queue, \
        self.tx_queue = getActiveNetCard()
        self.numa_node_core_range = getNUMA(self. bus_info)
        _, self.processor = getCPUInfo()

        logger.info("Network Card Info: \n \
        CPU:{}\n\
        dev:{}\n \
        interrupts queue:{}\n \
        rx queue: {} \n \
        tx queue: {} \n \
        numa_node_core:{}~{}".format(
            self.processor,
            self.dev_name,
            self.interrupts_queue, 
            self.rx_queue, 
            self.tx_queue,
            self.numa_node_core_range[0],
            self.numa_node_core_range[1]))

        self.backup_file = os.path.join(Config.BACNUP_PATH, "{}_backup.sh".format('net'))


    def _XPS_RPS_set(self, value, xps = True):
        """ Set XPS(Transmit Packet Steering)) and RPS(Receive Packet Steering)

        RPS Is in /sys/class/net/device/queues/rx-queue/rps_cpus Configure the receive queue in the file , among device Is the name of the network device (Such as eth0),rx-queue Is the name of the corresponding receive queue (Such as rx-0).

        rps_cpus The default value of the file is 0, That is to say, disable RPS, such CPU It can process data interrupt , Will also process packets .

        XPS By creating a CPU The corresponding relationship to the network card sending queue , To ensure the processing of sending soft interrupt requests CPU And sending out packets CPU Is the same CPU, It is used to ensure the locality when sending data packets.

        Adopt '/sys/class/net/<dev>/queues/tx-<n>/xps_cpus' File settings , The same is bitmaps The way .

        Args:
            value (str): XPS or RPS setting mode, i.e. different, off
        """
        if xps:
            _queue = self.tx_queue
            _set_cmd = XPS_SET
        else:
            _queue = self.rx_queue
            _set_cmd = RPS_SET
        
        # echo 00 > /sys/class/net/<dev>/queues/tx-<n>/xps_cpus
        if value == "off":
            for _index in range(min(self.processor,len(_queue))):
                suc, res = sysCommand(_set_cmd.format(
                    core_code = "0",
                    dev_name  = self.dev_name,
                    queue_id  = _queue[_index]
                ))
                if not suc:
                    return False, res
            return True, ""

        # echo 01 > /sys/class/net/<dev>/queues/tx-<n>/xps_cpus
        # echo 02 > /sys/class/net/<dev>/queues/tx-<n>/xps_cpus
        # echo 04 > /sys/class/net/<dev>/queues/tx-<n>/xps_cpus
        # ...
        if value == "different":
            for _index in range(min(self.processor,len(_queue))):
                _hex_code = hex(int("".join(
                        ['1' if j == _index else '0' \
                        for j in range(self.processor)][::-1]),2))[2:]

                suc, res = sysCommand(_set_cmd.format(
                    core_code = _hex_code,
                    dev_name  = self.dev_name,
                    queue_id  = _queue[_index]
                ))
                if not suc:
                    return False, res
            return True, ""


    def _smp_affinity_set(self, value):
        """ change the CPU specified to handle interrupts

        Args:
            value (str): CPU bonding mode. i.e. different, dedicated, off
        """

        if value == "dedicated":
            # shutdown the irqbalance service
            suc, res = sysCommand("systemctl stop irqbalance.service")
            if not suc:
                return False, "Failed to shutdown irqbalance.service"
            
            # moving interrupts to a dedicated CPU
            logger.info("moving interrupts to a dedicated CPU: {}".format(self.numa_node_core_range[0]))
            for queue_id in self.interrupts_queue:
                suc, res = sysCommand(SMP_AFFINITY_SET.format(
                    core_id  = self.numa_node_core_range[0],
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
                self.numa_node_core_range[0],self.numa_node_core_range[1]))
            
            for index, queue_id in enumerate(self.interrupts_queue):
                suc, res = sysCommand(SMP_AFFINITY_SET.format(
                    core_id  = self.numa_node_core_range[0] + index%(
                               self.numa_node_core_range[1] - self.numa_node_core_range[0]),
                    queue_id = queue_id
                ))
                if not suc:
                    return False, res
            return True, ""

        if value == "off":
            suc, res = sysCommand("systemctl restart irqbalance.service")
            for index, queue_id in enumerate(self.interrupts_queue):
                suc, res = sysCommand(SMP_AFFINITY_SET.format(
                    core_id  = "{}-{}".format(self.numa_node_core_range[0], self.numa_node_core_range[1]),
                    queue_id = queue_id
                ))
                if not suc:
                    return False, res
            return True, ""


    def setParamAll(self, param_list: dict):
        result = defaultdict(dict)
        success = False
        for param_name, param_info in param_list.items():
            if param_name.lower() == "xps":
                _suc, _res = self._XPS_RPS_set(param_info['value'], xps = True)
                
            elif param_name.lower() == "rps":
                _suc, _res = self._XPS_RPS_set(param_info['value'], xps = False)

            elif param_name.lower() == "smp_affinity":
                _suc, _res = self._smp_affinity_set(param_info['value'])
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


    def getParamAll(self, param_list: dict):
        result = defaultdict(dict)
        for param_name, param_info in param_list.items():
            result[param_name] = {
                "value" : "",
                "dtype" : param_info["dtype"],
                "suc"   : True,
                "msg"   : "This domain is not supported to parameter value reading."
            }
        return True, result
    

    def backup(self, param_list: dict):
        if os.path.exists(self.backup_file):
            self.rollback()
        
        rollback_script = ""
        
        for queue_id in self.interrupts_queue:
            suc, core_id = sysCommand(SMP_AFFINITY_GET.format(queue_id = queue_id))
            if not suc:
                return False, core_id
            rollback_script += SMP_AFFINITY_SET.format(core_id = core_id, queue_id = queue_id) + '\n'

        for tx_id in self.tx_queue:
            suc, core_code = sysCommand(XPS_GET.format(dev_name = self.dev_name, queue_id = tx_id))
            if not suc:
                return False, core_code
            rollback_script += XPS_SET.format(
                core_code = core_code,
                dev_name  = self.dev_name,
                queue_id  = tx_id
            ) + '\n'

        for rx_id in self.rx_queue:
            suc, core_code = sysCommand(RPS_GET.format(dev_name = self.dev_name, queue_id = rx_id))
            if not suc:
                return False, core_code
            rollback_script += RPS_SET.format(
                core_code = core_code,
                dev_name  = self.dev_name,
                queue_id  = rx_id
            ) + '\n'
        
        with open(self.backup_file, 'w') as f:
            f.write(rollback_script)
        
        return True, self.backup_file


    def rollback(self):
        if not os.path.exists(self.backup_file):
            return True, "Can not find backup file:{}".format(self.backup_file)

        suc ,res = sysCommand("bash {}".format(self.backup_file))
        if suc:
            backup_time = time.asctime(time.localtime(os.path.getctime(self.backup_file)))
            logger.info("Rollback to backup time: {}".format(backup_time))
            os.remove(self.backup_file)
            return True, backup_time
        else:
            logger.error("Failed to rollback: {}".format(res))
            return False, res


    def originalConfig(self, action):
        if action == "backup":
            return self.backup({})
        elif action == "rollback":
            return self.rollback()


if __name__ == "__main__":
    net = Net()
    print(net.setParamAll({"smp_affinity": {'value':'different','dtype':'str'}}))
    print(net.setParamAll({"smp_affinity": {'value':'dedicated','dtype':'str'}}))
    print(net.setParamAll({"smp_affinity": {'value':'off','dtype':'str'}}))

    print(net.setParamAll({"xps": {'value':'different','dtype':'str'}}))
    print(net.setParamAll({"xps": {'value':'off','dtype':'str'}}))

    print(net.setParamAll({"rps": {'value':'different','dtype':'str'}}))
    print(net.setParamAll({"rps": {'value':'off','dtype':'str'}}))

    print(net.backup({}))
    print(net.rollback())