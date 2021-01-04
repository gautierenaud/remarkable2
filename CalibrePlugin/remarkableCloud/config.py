__license__ = 'GPL v3'
__copyright__ = '2020, Renaud Tamon Gautier <gautierenaud at gmail.com>'

from calibre.utils.config import JSONConfig
from PyQt5.Qt import QLabel, QLineEdit, QVBoxLayout, QWidget

config = JSONConfig('plugins/remarkable_cloud')


def load() -> dict:
    return config


def dump(new_config: dict) -> None:
    global config
    config = new_config


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

    def validate(self):
        if self.registration_code.text():
            from calibre_plugins.remarkable_cloud.rmapy.api import Client
            rm_client = Client()
            return rm_client.register_device(self.registration_code.text())
        return True
