__license__ = 'GPL v3'
__copyright__ = '2020, Renaud Tamon Gautier <gautierenaud at gmail.com>'

from PyQt5.Qt import QLabel, QLineEdit, QVBoxLayout, QWidget
from calibre.utils.config import JSONConfig

config = JSONConfig('plugins/remarkable_ssh_driver')
config.defaults['devicetoken'] = None
config.defaults['usertoken'] = None
# cache used to match books between remarkable and calibre libraries.
# key = remarkable id, value = [calibre id, [authors]] (tuple was converted to list with JsonConfig)
config.defaults['match_cache'] = None


def load() -> dict:
    global config
    return config


def dump() -> None:
    global config
    config.commit()


class ConfigWidget(QWidget):

    def __init__(self, rm_client):
        QWidget.__init__(self)
        self.l = QVBoxLayout()
        self.setLayout(self.l)
        self.rm_client = rm_client

        if self.rm_client.is_registered():
            self.label = QLabel('Device is already registered')
            self.l.addWidget(self.label)
        else:
            self.label = QLabel(
                'Retrieve one-time registration code from <a href="https://my.remarkable.com/connect/remarkable">https://my.remarkable.com/connect/remarkable</a>:')
            self.label.setOpenExternalLinks(True)
            self.l.addWidget(self.label)

            self.registration_code = QLineEdit(self)
            self.l.addWidget(self.registration_code)
            self.label.setBuddy(self.registration_code)

    def validate(self):
        if self.rm_client.is_registered():
            return True

        # TODO: waiting screen when waiting for registration ?
        if self.registration_code.text():
            return self.rm_client.register_device(self.registration_code.text())
        return True

    def save_settings(self):
        dump()
