__license__ = 'GPL v3'
__copyright__ = '2020, Renaud Tamon Gautier <gautierenaud at gmail.com>'

from PyQt5.Qt import QWidget, QVBoxLayout, QLabel, QLineEdit
from calibre_plugins.remarkable_cloud.rmapy.config import config

if not 'book_dir' in config:
    config['book_dir'] = ''


class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.label = QLabel(
            'Retrieve one-time registration code from <a href="https://my.remarkable.com/connect/remarkable">https://my.remarkable.com/connect/remarkable</a>:')
        self.label.setOpenExternalLinks(True)
        self.l.addWidget(self.label)

        self.registration_code = QLineEdit(self)
        self.l.addWidget(self.registration_code)
        self.label.setBuddy(self.registration_code)

        self.book_dir_label = QLabel('Book directory:')
        self.l.addWidget(self.book_dir_label)

        self.book_dir = QLineEdit(self)
        self.book_dir.setText(config['book_dir'])
        self.l.addWidget(self.book_dir)
        self.book_dir_label.setBuddy(self.book_dir)

    def save_settings(self):
        config['book_dir'] = self.book_dir.text()

    def validate(self):
        if self.registration_code.text():
            from calibre_plugins.remarkable_cloud.rmapy.api import Client
            rm_client = Client()
            return rm_client.register_device(self.registration_code.text())
        return True
