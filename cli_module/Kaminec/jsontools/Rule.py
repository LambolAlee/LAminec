from .system import SYSNAME, SYSVERSION


class Rule:
    def __init__(self, rule_list, sysname=SYSNAME, sysversion=SYSVERSION):
        self.rule_list = rule_list
        self.sysname = sysname
        self.sysversion = sysversion
        self.allow = all(self.parseRule(each_rule) for each_rule in rule_list)

    def parseRule(self, each_rule):
        return self.assertWhetherAllow(each_rule)

    def assertWhetherAllow(self, each_rule):
        if each_rule["action"] == "disallow":
            #Assert Disallow
            allow = (self.sysname != each_rule["os"]["name"])
            return allow
        else:
            #Assert Allow
            return self.assertAllow(each_rule)

    def assertAllow(self, each_rule):
        try:
            allow = (self.sysname == each_rule["os"]["name"])
        except KeyError:
            allow = True
        if not allow:
            return allow
        try:
            pattern = each_rule["os"]["version"]
        except KeyError:
            allow = True
        else:
            allow = re.match(pattern, self.sysversion) if pattern else True
        return allow
