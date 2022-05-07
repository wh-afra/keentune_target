[English](./keentune-target/README.md)| [简体中文](./keentune-target/README_ch.md) 

# KeenTune Target  

## 简介
---  
KeenTune-target 业务侧优化设置组件，这是唯一必须部署在业务环境上的组件，用来设置静态或者动态调优生成的各项配置。其主要功能是在业务环境中执行参数设置、读取、备份和回滚等操作。

## 支持调优的参数
#### 内核参数-sysctl.conf
Domain name: sysctl
Requirements: None

#### Benchmark参数-iperf
Domain name: iperf
Requirements: Keentune-Bench安装在当前环境中

### 应用参数-Nginx
Domain name: nginx
Requirements: 当前环境中已安装Nginx, 当前环境中已安装pynginxconfig包


## 安装方法
---  
### 1. 安装 python-setuptools
```sh
$ sudo apt-get install python-setuptools
or
$ sudo yum install python-setuptools
```

### 2. 安装 keentune-target
```shell
$ sudo python3 setup.py install
```

### 3. 安装 requirements
```shell
$ pip3 install -r requirements.txt
```

### 4. 运行 keentune-target
```shell
$ keentune-target
```

## 代码结构
---  
+ common: 通用方法模块
+ controller: Web通信模块
+ domain: 参数领域定义和实现模块
+ scene: 调优场景定义和实现

## 文档