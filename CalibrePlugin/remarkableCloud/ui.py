#!/usr/bin/env python

__license__ = 'GPL v3'
__copyright__ = '2020, Renaud Tamon Gautier <gautierenaud at gmail.com>'

from calibre.gui2.actions import InterfaceAction
from PyQt5.Qt import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel


class rMCloudPlugin(InterfaceAction):
    name = 'reMarkable Cloud Plugin'

    action_spec = ('Sync reMarkable', None,
                   'Synchronize calibre with reMarkable\'s cloud', None)

    def genesis(self):
        icon = get_icons('images/icon.png')

        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.list_documents)
    
    def list_documents(self):
        from calibre_plugins.remarkable_cloud.rmapy.api import Client
        rm_client = Client()
        rm_client.renew_token()
        print(rm_client.get_meta_items())