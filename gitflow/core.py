from git import Repo
from ConfigParser import NoOptionError, NoSectionError, DuplicateSectionError, \
                         MissingSectionHeaderError, ParsingError


class NotInitialized(Exception):
    pass


class GitFlow(object):
    def __init__(self, repo):
        self.repo = repo

    def init(self,
            master=None, develop=None,
            feature=None, release=None, hotfix=None,
            support=None, force_defaults=False):
        defaults = [
            ('gitflow.branch.master', 'master', master),
            ('gitflow.branch.develop', 'develop', develop),
            ('gitflow.prefix.feature', 'feature/', feature),
            ('gitflow.prefix.release', 'release/', release),
            ('gitflow.prefix.hotfix', 'hotfix/', hotfix),
            ('gitflow.prefix.support', 'support/', support),
        ]
        for setting, default, value in defaults:
            if not value is None:
                self.set(setting, value)
            else:
                if force_defaults or not self.is_set(setting):
                    self.set(setting, default)

    def is_initialized(self):
        return self.is_set('gitflow.branch.master') \
           and self.is_set('gitflow.branch.develop') \
           and self.is_set('gitflow.prefix.feature') \
           and self.is_set('gitflow.prefix.release') \
           and self.is_set('gitflow.prefix.hotfix') \
           and self.is_set('gitflow.prefix.support')


    def _parse_setting(self, setting):
        groups = setting.split('.', 2)
        if len(groups) == 2:
            subsection = None
            section, option = groups
        elif len(groups) == 3:
            section, subsection, option = groups
        else:
            raise ValueError('Invalid setting name: %s' % setting)

        if subsection:
            section = '%s "%s"' % (section, subsection)
        else:
            section = section

        return (section, option)

    def get(self, setting, default=None, null=False):
        section, option = self._parse_setting(setting)
        try:
            setting = self.repo.config_reader().get(section, option)
            return setting
        except (NoSectionError, DuplicateSectionError, NoOptionError,
                MissingSectionHeaderError, ParsingError):
            if null:
                return None
            elif not default is None:
                return default
            raise

    def set(self, setting, value):
        section, option = self._parse_setting(setting)
        writer = self.repo.config_writer()
        if not section in writer.sections():
            writer.add_section(section)
        writer.set(section, option, value)

    def is_set(self, setting):
        return not self.get(setting, null=True) is None


    def _safe_get(self, setting_name):
        try:
            return self.get(setting_name)
        except NoSectionError, NoOptionError:
            raise NotInitialized('This repo has not yet been initialized.')

    def master(self):
        return self._safe_get('gitflow.branch.master')

    def develop(self):
        return self._safe_get('gitflow.branch.develop')

    def feature_prefix(self):
        return self._safe_get('gitflow.prefix.feature')

    def hotfix_prefix(self):
        return self._safe_get('gitflow.prefix.hotfix')

    def release_prefix(self):
        return self._safe_get('gitflow.prefix.release')

    def support_prefix(self):
        return self._safe_get('gitflow.prefix.support')


    def feature_branches(self):
        return [h.name for h in self.repo.heads \
                    if h.name.startswith(self.feature_prefix())]
