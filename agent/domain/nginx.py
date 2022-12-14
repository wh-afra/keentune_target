import os
from pynginxconfig import NginxConfig

from agent.common.config import Config
from agent.common.system import sysCommand
from agent.common.pylog import functionLog


class Nginx:
    def __init__(self):
        """init nginx domain

        1. init NginxConfig obj.
        2. start nginx service.
        """
        self.nginx_config_path = "/etc/nginx/nginx.conf"
        self.backup_file = os.path.join(Config.BACNUP_PATH, "nginx_backup.conf")

        self.nginx_conf = NginxConfig()
        suc, msg = self._restart()
        if not suc:
            raise Exception(msg)

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

        except KeyError:
            return False, "No such parameter as {}".format(param_name)

        except TypeError:
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

        except KeyError:
            return False, "No such parameter as {}".format(param_name)

        else:
            return True, ""

    @functionLog
    def getParamAll(self, param_list):
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
    def setParamAll(self, param_list):
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
        if self.nginx_conf.get([("http",), "log_format"]):
            self.nginx_conf.set([("http",), "log_format"], log_value)
        if self.nginx_conf.get([("http",), "access_log"]):
            self.nginx_conf.set([("http",), "access_log"], "off")

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
    def backup(self, _):
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

    def originalConfig(self, action):
        """ backup or rollback original configuration

        Args:
            action (str): rollback or backup

        Returns:
            bool: if success.
            str : operating or error messages.
        """
        @functionLog
        def __backupOriginalConfig():
            # TODO: risk of missing backup of nginx config if user started keentune-target before nginx service
            # suc, _ = sysCommand("systemctl status nginx")
            # if suc == 4:
            #     return True, "No nginx service is found. No configuration backup is required"

            if os.path.exists(os.path.join(Config.ORIGINAL_CONF_PATH, os.path.split(config_to_backup)[1])):
                return True, "backup file:{} exists, no need to backup again".format(
                    os.path.join(Config.ORIGINAL_CONF_PATH, os.path.split(config_to_backup)[1]))

            if not os.path.exists(config_to_backup):
                return True, "The application does not require a configuration file"

            return sysCommand("cp -f {} {}".format(config_to_backup, Config.ORIGINAL_CONF_PATH))

        @functionLog
        def __rollbackOriginalConfig():
            if not os.path.exists(os.path.join(Config.ORIGINAL_CONF_PATH, os.path.split(config_to_backup)[1])):
                return True, "No backup file was found"

            suc, msg = sysCommand("mv -f {} {}".format(
                os.path.join(Config.ORIGINAL_CONF_PATH, os.path.split(config_to_backup)[1]),
                os.path.split(config_to_backup)[0]
            ))
            if not suc:
                return False, "Failed to mv backup file to {}: {}".format(os.path.split(config_to_backup)[0], msg)

            suc, msg = sysCommand("systemctl restart nginx")
            if not suc:
                return False, "Failed to restart nginx: {}".format(msg)

            return True, ""

        assert action in ['backup', 'rollback']
        config_to_backup = "/etc/nginx/nginx.conf"

        if action == "backup":
            return __backupOriginalConfig()
        
        elif action == "rollback":
            return __rollbackOriginalConfig()