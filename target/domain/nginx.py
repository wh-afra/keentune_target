import os

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
        self.backup_file = os.path.join(Config.backup_dir, "nginx_backup.conf")

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
                res = self.nginx_conf.get([('events',), param_name])

            else:
                res = self.nginx_conf.get([('http',), param_name])

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
    def _appendParam(self, param, item):
        """ Append a parameter and value to nginx.conf

        Args:
            param (str) : main module of nginx.conf
            item (tuple): the name and value of the parameter.

        Returns:
            bool: whether success to append parameter and value.
            str : fail message.
        """
        try:
            position_dict = {"events": 1, "http": 7}
            position = position_dict[param]
            for index, element in enumerate(self.nginx_conf.data):
                if isinstance(element, dict) and element["name"] == param:
                    self.nginx_conf.data[index]["value"].insert(position, item)

        except Exception as err:
            return False, "append parameter failed, error is:{}".format(err)

        return True, ""

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
                if self.nginx_conf.get(param_name):
                    self.nginx_conf.set(param_name, param_value)
                else:
                    self.nginx_conf.append(
                        (param_name, param_value), position=4)

            elif param_name in ["worker_connections", "multi_accept"]:
                if self.nginx_conf.get([("events",), param_name]):
                    self.nginx_conf.set([("events",), param_name], param_value)
                else:
                    self._appendParam("events", (param_name, param_value))

            else:
                if self.nginx_conf.get([("http",), param_name]):
                    self.nginx_conf.set([("http",), param_name], param_value)
                else:
                    self._appendParam("http", (param_name, param_value))

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
        log_value = """main  '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"'"""
        self.nginx_conf.set([("http",), "log_format"], log_value)

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

        1. Copy parameter values from backup file to nginx.conf
        2. restart nginx service if success to rollback nginx.conf. 

        Returns:
            bool: whether success to rollback.
            str : fail message.
        """
        if not os.path.exists(self.backup_file):
            return True, "backup file {} do not exists.".format(self.backup_file)

        suc, res = sysCommand("echo y | cp {} {}".format(
            self.backup_file, self.nginx_config_path))
        if not suc:
            return False, "rollback nginx config failed:{}".format(res)

        suc, msg = self._restart()
        if not suc:
            return False, "restart Nginx failed:{}".format(msg)

        os.remove(self.backup_file)
        return True, "rollback nginx conf successfully!"

    @functionLog
    def backup(self, param_list: dict):
        """ Backup parameter values in nginx.conf to backup files.

        Copy parameter values from nginx.conf to backup file as .conf

        Returns:
            bool: whether success to backup.
            str : fail message.
        """
        if os.path.exists(self.backup_file):
            suc, res = self.rollback()
            if not suc:
                return False, res

        suc, res = sysCommand("echo y | cp {} {}".format(
            self.nginx_config_path, self.backup_file))
        if not suc:
            return False, "backup nginx conf failed:{}".format(res)

        return True, "backup nginx successfully!"
