import re
import subprocess

from agent.common.pylog import functionLog, logger


@functionLog
def sysCommand(command: str, cwd: str = "./"):
    '''Run system command with subprocess.run and return result
    '''
    logger.info(command)
    result = subprocess.run(
        command,
        shell=True,
        close_fds=True,
        cwd=cwd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    suc = (result.returncode == 0)
    out = result.stdout.decode('UTF-8', 'strict').strip()
    error = result.stderr.decode('UTF-8', 'strict').strip()

    if not suc:
        logger.error(error)
        return suc, error
    else:
        return suc, out


def getActiveNetCard():
    """ get active networkcard name, pci number and bus info

    Returns:
        str: networkcard name
        str: pci number
        str: bus info
    """
    suc, netcard_list = sysCommand("cat /proc/net/dev")
    if not suc:
        return
    
    netcard_list = netcard_list.split('\n')[2:]
    netcard_list_receive = sorted(
        [[j for j in re.split(r"[: ]",i) if j != ''][:2] for i in netcard_list], 
        key=lambda x:x[1]
    )

    # 'virtio2' is the network card name in virt env
    netcard_list_receive.append(['virtio2', 0])

    for dev_name, _ in netcard_list_receive:
        suc, _pci_number = sysCommand("ethtool -i {}".format(dev_name))
        if not suc:
            continue
        bus_info = re.search(r"bus-info: (.*)\n", _pci_number).group(1)
        if bus_info == '':
            continue

        suc, _interrupts_info = sysCommand(
            "cat /proc/interrupts | grep {dev_name}".format(dev_name = dev_name))
        if not suc:
            continue
        interrupts_queue = [
            [j for j in re.split(r"[: ]",i) if j != ""][0] 
            for i in _interrupts_info.split('\n')
        ]

        suc, queue_info = sysCommand(
            "ls /sys/class/net/{dev_name}/queues/".format(dev_name = dev_name))
        if not suc:
            continue
        rx_queue, tx_queue = re.findall(r"rx-\d",queue_info), re.findall(r"tx-\d",queue_info)

        return dev_name, bus_info, interrupts_queue, rx_queue, tx_queue

    return


def getNUMA(bus_info):
    suc, numa_message = sysCommand("lspci -vvvs {bus_info}".format(bus_info = bus_info))
    if not suc:
        return 
    numa_node_num = re.search(r"NUMA node: (\d)\n", numa_message).group(1)
    if numa_node_num == '':
        return
    _, cpu_message = sysCommand("lscpu")
    if re.search(r"NUMA node{} CPU\(s\):\s*(\d+-\d+)".format(numa_node_num),cpu_message):
        numa_node_core_range = re.search(
            r"NUMA node{} CPU\(s\):\s*(\d+-\d+)".format(numa_node_num),cpu_message).group(1).split('-')
    else:
        return
    numa_node_core_range = [int(i) for i in numa_node_core_range]
    return numa_node_core_range


def getCPUInfo():
    _, cpu_num   = sysCommand("cat /proc/cpuinfo| grep 'physical id'| sort| uniq| wc -l")
    _, processor = sysCommand("cat /proc/cpuinfo| grep 'processor'| wc -l")
    return int(cpu_num), int(processor)


if __name__ == "__main__":
    dev_name, bus_info, interrupts_queue, rx_queue, tx_queue = getActiveNetCard()
    print("dev_name:", dev_name)
    print("bus_info:", bus_info)
    print("interrupts_queue:", interrupts_queue)
    print("rx_queue:", rx_queue)
    print("tx_queue:", tx_queue)

    numa_node_core_range = getNUMA(bus_info)
    print("numa_node_core_range: ", numa_node_core_range)

    cpu_num, cpu_core, processor = getCPUInfo()
    print("cpu_num:", cpu_num)
    print("cpu_core:", cpu_core)
    print("processor:", processor)