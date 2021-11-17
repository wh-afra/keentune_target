import os
import yaml

from pynginxconfig import NginxConfig

from target.common.config import Config
from target.common.system import sysCommand
from target.common.pylog import functionLog


class Nginx:
    def __init__(self):
        """init nginx domain

        1. init NginxConfig obj.
        2. start nginx service.
        """
        super().__init__()
        self.nginx_config_path = "/etc/nginx/nginx.conf"
        self.backup_file = os.path.join(Config.backup_dir,"nginx_backup.yaml")

        self.nginx_conf = NginxConfig()
        self._restart()


    @functionLog
    def _restart(self):
        """ Restart nginx service

        Returns:
            bool: whether success to restart nginx service.
            str : fail message.
        """
        suc, res = sysCommand("systemctl restart nginx")
        if not suc:
            return False, "run restart nginx commond failed:{}".format(res)
        
        return True, ""
    

    @functionLog
    def _getParam(self, param_name):
        """ Read value of a parameter in nginx.conf

        Args:
            param_name (string): parameter name.

        Returns:
            bool: whether success to read parameter value.
            str : parameter value or fail message.
        """
        try:
            if param_name in ["worker_processes", "worker_rlimit_nofile"]:
                res = self.nginx_conf.get(param_name)

            elif param_name in ["worker_connections", "multi_accept"]:
                res = self.nginx_conf.get([('events',), (param_name)])

            else:
                res = self.nginx_conf.get([('http',), (param_name)])
            
            if res is None:
                return True, ""
            else: 
                param_value = res[1]
                return True, param_value

        except KeyError as e:
            return False, "No such parameter as {}".format(param_name)

        except TypeError as e:
            return False, "No such parameter as {}".format(param_name)


    @functionLog
    def _setParam(self, param_name, param_value):
        """ Set value of a parameter in nginx.conf

        Args:
            param_name (str) : parameter name.
            param_value (str): parameter value to set.

        Returns:
            bool: whether success to set parameter value.
            str : fail message.
        """
        if param_name == '' or param_value == '':
            return True, ""
        try:
            param_value = "{}".format(param_value).strip()
            if param_name in ["worker_processes", "worker_rlimit_nofile"]:
                self.nginx_conf.set(param_name, param_value)

            elif param_name in ["worker_connections", "multi_accept"]:
                self.nginx_conf.set([('events',), (param_name)], param_value)

            else:
                self.nginx_conf.set([('http',), (param_name)], param_value)

        except KeyError as e:
            return False, "No such parameter as {}".format(param_name)

        else:
            return True, ""


    @functionLog
    def getParamAll(self, param_list: dict):
        """ Read value of parameters.

        Args:
            param_list (dict): parameters list.

        Returns:
            bool: whether success to get parameters value.
            obj : result dictionary or error message
        """
        self.nginx_conf.loadf(self.nginx_config_path)

        result = {}
        for param_name in param_list.keys():
            suc, param_value = self._getParam(param_name)
            result[param_name] = {
                "value": "{}".format(param_value).replace("\t", " "), 
                "dtype": "", 
                "suc": True, 
                "msg": ""
            }
        return True, result


    @functionLog
    def setParamAll(self, param_list: dict):
        """ Set value of parameters.

        if success to set parameters, restart nginx service.

        Args:
            param_list (dict): parameters list.

        Returns:
            bool: whether success to set parameters value.
            obj : result dictionary or error message
        """
        self.nginx_conf.loadf(self.nginx_config_path)

        result = {}
        for param_name, param_info in param_list.items():
            suc, msg = self._setParam(param_name, param_info["value"])
            result[param_name] = {
                "value": param_info["value"],
                "dtype": param_info["dtype"],
                "suc": suc,
                "msg": msg
            }

        self.nginx_conf.savef(self.nginx_config_path)
        
        suc, msg = self._restart()
        if not suc:
            return False, "restart Nginx failed:{}".format(msg)
        return True, result


    @functionLog
    def rollback(self):
        """ rollback parameter values in nginx.conf.

        1. Read parameter values from backup files.
        2. Set parameter values to nginx.conf.
        3. restart nginx service if success to rollback nginx.conf. 

        Returns:
            bool: whether success to rollback.
            str : fail message.
        """
        if not os.path.exists(self.backup_file):
            return True, "backup file {} do not exists.".format(self.backup_file)
    
        with open(self.backup_file) as f:
            backup_content = yaml.safe_load(f)

        rollback_suc = True
        rollback_msg = ""

        self.nginx_conf.loadf(self.nginx_config_path)
        for param_name, param_value in backup_content.items():
            suc, msg = self._setParam(param_name, param_value)
            if not suc:
                rollback_suc = False
                rollback_msg += msg + "\n"
        self.nginx_conf.savef(self.nginx_config_path)

        if not rollback_suc:
            return False, rollback_msg

        suc, msg = self._restart()
        if not suc:
            return False, "restart Nginx failed:{}".format(msg)

        return True, "rollback nginx conf successfully!"


    @functionLog
    def backup(self, param_list: dict):
        """ Backup parameter values in nginx.conf to backup files.

        1. Read parameter values from nginx.conf
        2. Set parameter values to backup file as .yaml

        Returns:
            bool: whether success to backup.
            str : fail message.
        """
        self.nginx_conf.loadf(self.nginx_config_path)

        backup_content = {}
        for param_name in param_list.keys():
            suc, param_value = self._getParam(param_name)
            if not suc:
                return False, "backup parameter {} failed:{}".format(
                                param_name, param_value)
            if param_value == '':
                continue
            backup_content[param_name] = param_value

        with open(self.backup_file, "w", encoding="utf-8") as f:
            yaml.dump(backup_content, f)

        return True, "backup vm_nginx successfully!"