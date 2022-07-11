# KeenTune Target  
---  

### Introduction
KeenTune-target is the optimization setting component, which is the only component of KeenTune that needs to be deployed in business environments. It is used to set optimized settings in dynamic and static tuning workflows, with operations such as parameter set, get, backup, and rollback.

### Build & Install
Setuptools can build KeenTune-target as a python lib. We can run setuptools as  
```s
>> pip3 install setuptools
>> python3 setup.py install
>> pip3 install -r requirements.txt
```

### Configuration
After install KeenTune-target by setuptools or pyInstaller, we can find configuration file in **/etc/keentune/conf/target.conf**
```conf
[agent]
# Basic Configuration
KeenTune_HOME       = /etc/keentune/                ; KeenTune-target install path.
KeenTune_WORKSPACE  = /var/keentune/                ; KeenTune-target workspace.
AGENT_PORT          = 9873                          ; KeenTune-target service port
ORIGINAL_CONF       = /var/keentune/OriginalBackup  ; Original configuration backup path.

[log]
# Configuration about log
LOGFILE_PATH        = /var/log/keentune/target.log  ; Log file of target
CONSOLE_LEVEL       = INFO                          ; Console Log level
LOGFILE_LEVEL       = DEBUG                         ; File saved log level
LOGFILE_INTERVAL    = 1                             ; The interval of log file replacing
LOGFILE_BACKUP_COUNT= 14                            ; The count of backup log file  
```

### Run
After modify KeenTune-target configuration file, we can deploy KeenTune-target and listening to requests as 
```s
>> keentune-target
```
or depoly KeenTune-target by systemctl  
```s
>> systemctl start keentune-target
```
**NOTE**: You need copy the file 'keentune-target.service' to '/usr/lib/systemd/system' manually, if you installed the keentune-target by 'setuptools' rather then 'yum install'.  

---   
### Code Structure
```
agent/
├── agent.py            # Entrance of keentune-target
├── common              # Common module, includes log, config and tools.
│   ├── config.py
│   ├── __init__.py
│   ├── pylog.py
│   └── system.py
├── controller          # Service response module.
│   ├── backup.py
│   ├── configure.py
│   ├── detect.py
│   ├── __init__.py
│   ├── orig_conf.py
│   ├── rollback.py
│   └── status.py
├── domain              # knobs domain
│   ├── __init__.py
│   ├── iperf.py
│   ├── nginx.py
│   ├── sysbench.py
│   └── sysctl.py
├── __init__.py
└── target.conf          # Configuration file

3 directories, 19 files
```