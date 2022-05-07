[English](./keentune-target/README.md)| [简体中文](./keentune-target/README_ch.md) 

# KeenTune Target  

## Introduction
---  
KeenTune-target is the optimization setting component, which is the only component of KeenTune that needs to be deployed in business environments. It is used to set optimized settings in dynamic and static tuning workflows, with operations such as parameter set, get, backup, and rollback.

## supported parameters domain
#### OS kernel-sysctl.conf
Domain name: sysctl
Requirements: None

#### Benchmark knobs-iperf
Domain name: iperf
Requirements: 
+ Keentune-Bench already installed in current environment

### Application parameters-Nginx
Domain name: nginx
Requirements: 
+ Nginx server already installed in current environment
+ pynginxconfig package already installed in current environment

## Installation
---  
### 1. install python-setuptools
```sh
$ sudo apt-get install python-setuptools
or
$ sudo yum install python-setuptools
```

### 2. install keentune-target
```shell
$ sudo python3 setup.py install
```

### 3. install requirements
```shell
$ pip3 install -r requirements.txt
```

### 4. run keentune-target
```shell
$ keentune-target
```

## Code structure
---  
+ common: common methods
+ controller: Web communication module.
+ domain: Parameter domain definition and realization module
+ scene: Parameter scene definition and realization module

## Documentation