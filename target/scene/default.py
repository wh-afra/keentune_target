from target.common.pylog import functionLog
from target.domain import sysctl


class DefaultScene:
    Domain = {
        "sysctl": sysctl.Sysctl(),
    }

    Domain_Priority = {
        "sysctl": 1,
    }

    def __init__(self):
        super().__init__()

    @functionLog
    def paramSet(self, param_domain_dict: dict):
        domain_result = {}
        SUC = True

        for domain in sorted(self.Domain_Priority,
                             key=lambda x: self.Domain_Priority[x]):
            if not param_domain_dict.__contains__(domain):
                continue

            param_list = param_domain_dict[domain]

            suc, res = self.Domain[domain].setParamAll(param_list)
            SUC = SUC or suc

            domain_result[domain] = res

        return SUC, domain_result

    @functionLog
    def paramGet(self, param_domain_dict: dict):
        domain_result = {}
        SUC = True

        for domain in sorted(self.Domain_Priority,
                             key=lambda x: self.Domain_Priority[x]):
            if not param_domain_dict.__contains__(domain):
                continue
            param_list = param_domain_dict[domain]

            suc, res = self.Domain[domain].getParamAll(param_list)
            SUC = SUC or suc

            domain_result[domain] = res

        return SUC, domain_result

    @functionLog
    def rollback(self):
        domain_result = {}
        SUC = True

        for domain in sorted(self.Domain_Priority,
                             key=lambda x: self.Domain_Priority[x]):

            suc, res = self.Domain[domain].rollback()
            SUC = SUC or suc

            domain_result[domain] = res

        return suc, domain_result

    @functionLog
    def backup(self, param_domain_dict: dict):
        domain_result = {}
        SUC = True

        for domain in sorted(self.Domain_Priority,
                             key=lambda x: self.Domain_Priority[x]):
            if not param_domain_dict.__contains__(domain):
                continue
            param_list = param_domain_dict[domain]

            suc, res = self.Domain[domain].rollback()
            SUC = SUC and suc
            domain_result[domain] = res

            suc, res = self.Domain[domain].backup(param_list)
            SUC = SUC and suc

            domain_result[domain] = res

        return SUC, domain_result
