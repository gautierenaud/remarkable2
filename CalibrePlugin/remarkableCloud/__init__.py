#!/usr/bin/env python

__license__ = 'GPL v3'
__copyright__ = '2020, Renaud Tamon Gautier <gautierenaud at gmail.com>'

from calibre.customize import InterfaceActionBase


class RemarkableCloud(InterfaceActionBase):
    name = 'Remarkable Cloud Plugin'
    description = 'Connects Calibre with Remarkable Cloud'
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Renaud Tamon Gautier'
    version = (0, 1, 0)

    actual_plugin = 'calibre_plugins.remarkable_cloud.ui:rMCloudPlugin'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.remarkable_cloud.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
