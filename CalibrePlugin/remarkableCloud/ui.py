#!/usr/bin/env python

__license__ = 'GPL v3'
__copyright__ = '2020, Renaud Tamon Gautier <gautierenaud at gmail.com>'

from calibre.gui2 import error_dialog
from calibre.gui2.actions import InterfaceAction
from PyQt5.Qt import QDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout


class IncompatibleFormatError(Exception):
    def __init__(self, expected_formats, actual_formats):
        self.expected_formats = expected_formats
        self.actual_formats = actual_formats


class rMCloudPlugin(InterfaceAction):
    name = 'reMarkable Cloud Plugin'

    action_spec = ('Sync reMarkable', None,
                   'Synchronize calibre with reMarkable\'s cloud', None)

    def genesis(self):
        icon = get_icons('images/icon.png')

        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.list_documents)

    def _get_selected_ids(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            d = error_dialog(
                self.gui, 'Sync books with reMarkable Cloud', _('No book selected'))
            d.exec_()
            return set()
        return set(map(self.gui.library_view.model().id, rows))

    def list_documents(self):
        from calibre_plugins.remarkable_cloud.rmapy.api import Client
        from calibre_plugins.remarkable_cloud.rmapy.document import ZipDocument
        rm_client = Client()
        rm_client.renew_token()

        db = self.gui.current_db.new_api

        ids = self._get_selected_ids()
        for id in ids:
            formats = db.formats(id)
            if 'EPUB' in formats:
                fmt = 'EPUB'
            elif 'PDF' in formats:
                fmt = 'PDF'
            else:
                raise IncompatibleFormatError(('EPUB','PDF'), formats)

            file_path = db.format_abspath(id, fmt)
            zip_doc = ZipDocument(doc=file_path)
            res = rm_client.upload(zip_doc)
            print(res)
