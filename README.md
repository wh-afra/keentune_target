# KeenTune Target  

## Introduction
---  
KeenTune-target is the optimization setting component, which is the only component of KeenTune that needs to be deployed in business environments. It is used to set optimized settings in dynamic and static tuning workflows, with operations such as parameter set, get, backup, and rollback.

## Build & Install
### By setuptools
Setuptools can build target as a python lib. We can run setuptools as  
```s
>> python3 setup.py install
```

### By pyInstaller
pyInstaller can build KeenTune-target as a binary file. We can run pyInstaller as  
```s
>> make
>> make install
```

### Configuration
After install KeenTune-target by setuptools or pyInstaller, we can find configuration file in **/etc/keentune/conf/target.conf**
```conf
[agent]
KEENTUNE_HOME = /etc/keentune/                  # KeenTune-target install path.
KEENTUNE_WORKSPACE = /var/keentune/             # KeenTune-target user file workspace.
ORIGINAL_CONF = /var/keentune/OriginalBackup    # Original Configuration backup path.
AGENT_PORT = 9873                               # KeenTune-target listening port.

[log]
CONSOLE_LEVEL = ERROR                           # Log level of console.
LOGFILE_LEVEL = DEBUG                           # Log level of logfile.
LOGFILE_PATH  = /var/log/keentune/target.log    # Logfile saving path.
LOGFILE_INTERVAL = 1                            
LOGFILE_BACKUP_COUNT = 14
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

## Build a rpm
### By setuptools
### By pyInstaller