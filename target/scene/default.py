import os
import json

from target.common.config import Config
from target.common.pylog import functionLog
from target.domain import sysctl
from target.domain import nginx


class DefaultScene:
    Domain = {
        "sysctl": sysctl.Sysctl(),
        "nginx_conf": nginx.Nginx()
    }

    Domain_Priority = {
        "sysctl": 1,
        "nginx_conf": 2
    }

    def __init__(self):
        super().__init__()

    @functionLog
    def _reboot(self):
        return True, ""

    @functionLog
    def _init(self):
        return True, ""

    @functionLog
    def paramSet(self, param_domain_dict: dict):
        self._init()

        domain_result = {}
        failed = False

        for domain in sorted(self.Domain_Priority,
                             key=lambda x: self.Domain_Priority[x]):

            if not param_domain_dict.__contains__(domain):
                continue
            param_list = param_domain_dict[domain]

            # Backup parameters to set.
            suc, res = self.Domain[domain].backup(param_list)
            if not suc:
                failed = True
                domain_result[domain] = res
                continue

            # Set parameter values.
            suc, res = self.Domain[domain].setParamAll(param_list)
            if not suc:
                failed = True
                domain_result[domain] = res
                continue

            # Check parameters setting result.
            suc, res = self.Domain[domain].getParamAll(param_list)
            if not suc:
                failed = True
            domain_result[domain] = res

        self._reboot()
        return (not failed), domain_result

    @functionLog
    def paramGet(self, param_domain_dict: dict):
        domain_result = {}
        failed = False

        for domain in sorted(self.Domain_Priority,
                             key=lambda x: self.Domain_Priority[x]):
            if not param_domain_dict.__contains__(domain):
                continue
            param_list = param_domain_dict[domain]

            suc, res = self.Domain[domain].getParamAll(param_list)
            if not suc:
                failed = True
            domain_result[domain] = res

        return (not failed), domain_result

    @functionLog
    def rollback(self):
        self._init()

        domain_result = {}
        suc = True

        for domain in sorted(self.Domain_Priority,
                             key=lambda x: self.Domain_Priority[x]):

            suc, res = self.Domain[domain].rollback()
            if not suc:
                suc = False
            domain_result[domain] = res

        self._reboot()
        return suc, domain_result

    @functionLog
    def backup(self, param_domain_dict: dict):
        domain_result = {}
        suc = True

        for domain in sorted(self.Domain_Priority,
                             key=lambda x: self.Domain_Priority[x]):
            if not param_domain_dict.__contains__(domain):
                continue
            param_list = param_domain_dict[domain]

            suc, res = self.Domain[domain].rollback()
            if not suc:
                suc = False
            domain_result[domain] = res

            suc, res = self.Domain[domain].backup(param_list)
            if not suc:
                suc = False

            domain_result[domain] = res

        return suc, domain_result
