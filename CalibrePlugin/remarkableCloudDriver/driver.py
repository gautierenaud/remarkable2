#!/usr/bin/env python

__license__ = 'GPL v3'
__copyright__ = '2021, Renaud Tamon Gautier <gautierenaud at gmail.com>'
__docformat__ = 'restructuredtext en'

'''
Driver for remarkable 2 tablets, but using the cloud api provided by remarkable. May work on the first gen as well, but
not tested.
'''

import inspect
import logging
import sys
import time

from calibre.devices.usbms.device import Device
from calibre_plugins.remarkable_cloud_driver.config import config, ConfigWidget, dump

logger = logging.getLogger("mechanize")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


class RemarkableCloudDriver(Device):
    name = 'Remarkable 2 Cloud Interface'
    gui_name = 'Remarkable 2'
    description = _('Communicate with Remarkable\'s Cloud API')
    author = 'Renaud Tamon GAUTIER'
    version = (0, 0, 1)

    # only tested on linux though...
    supported_platforms = ['windows', 'osx', 'linux']

    FORMATS = ['epub', 'pdf']

    MANAGES_DEVICE_PRESENCE = True

    def __init__(self, args):
        super().__init__(args)
        self.report_progress = lambda x, y: None
        self.rm_client = None
        # the refresh of the device's library after a deletion will be too quick, before the deletion actually takes
        # place. So we have to maintain a list of books to ignore
        self.ignore_books = set()

    def startup(self):
        from calibre_plugins.remarkable_cloud_driver.rmapy.api import Client
        self.rm_client = Client()
        # debug
        if self.rm_client.is_auth():
            logger.debug('authenticated')
        else:
            logger.debug('not authenticated')

        # had to init by hand, the default value will not make match_cache appear.
        if not config['match_cache']:
            config['match_cache'] = {}

    def is_customizable(self):
        return True

    def config_widget(self):
        # from calibre_plugins.remarkable_cloud_driver.config import ConfigWidget
        return ConfigWidget(self.rm_client)

    def save_settings(self, config_widget):
        config_widget.save_settings()

    def detect_managed_devices(self, devices_on_system, force_refresh=False):
        # TODO: should be registered through plugin settings, display a message ?
        if not self.rm_client.is_registered():
            return None

        if not self.rm_client.is_auth():
            self.rm_client.renew_token()

        return self if self.rm_client.is_auth() else None

    def debug_managed_device_detection(self, devices_on_system, output):
        if self.rm_client.is_auth():
            from calibre_plugins.remarkable_cloud_driver.rmapy.const import DEVICE, USER_AGENT
            output.write(f'Connected to remarkable cloud as: {DEVICE}, {USER_AGENT}')
            return True
        return False

    def open(self, connected_device, library_uuid):
        # since it is a connection to a cloud, nothing to be done here
        logger.debug('open remarkable device')

    def set_progress_reporter(self, report_progress):
        self.report_progress = report_progress

    def get_device_information(self, end_session=True):
        return 'remarkable cloud', '0.0.1', 'whatever', ''

    def is_running(self):
        print('#######' + inspect.currentframe().f_code.co_name)
        return True

    def reset(self, key='-1', log_packets=False, report_progress=None, detected_device=None):
        print('#######' + inspect.currentframe().f_code.co_name)
        pass

    def eject(self):
        print('#######' + inspect.currentframe().f_code.co_name)
        pass

    def post_yank_cleanup(self):
        print('#######' + inspect.currentframe().f_code.co_name)
        pass

    def card_prefix(self, end_session=True):
        return None, None

    def total_space(self, end_session=True):
        return 10e9, 0, 0

    def free_space(self, end_session=True):
        return 9e9, 0, 0

    def books(self, oncard=None, end_session=True):
        print('#######' + inspect.currentframe().f_code.co_name)

        from calibre.devices.usbms.books import BookList
        booklist = BookList(oncard, None, None)

        # since it is a cloud connection, there is no such thing as memory card
        if oncard:
            return booklist

        self.rm_client.renew_token()
        meta_items = self.rm_client.get_meta_items()
        folders = filter(lambda x: x.Type == 'CollectionType', meta_items)
        documents = filter(lambda x: x.Type == 'DocumentType', meta_items)

        doc_hierarchy = {folder.ID: (folder.VissibleName, folder.Parent) for folder in folders}

        def get_full_hierarchy(parent_id):
            full_path = doc_hierarchy[parent_id][0] if parent_id in doc_hierarchy else ""
            parent_id = doc_hierarchy[parent_id][1] if parent_id in doc_hierarchy else None
            while parent_id in doc_hierarchy:
                full_path = doc_hierarchy[parent_id][0] + '/' + full_path
                parent_id = doc_hierarchy[parent_id][1]
            return full_path

        for doc in documents:
            if doc.ID in self.ignore_books:
                continue

            # very ugly hack, but the date has variable size (sometime millisec is missing) and is timezoned
            datetime = time.strptime(doc.ModifiedClient.split('.')[0].replace('Z', ''), '%Y-%m-%dT%H:%M:%S')

            b = Book(title=doc.VissibleName, rm_id=doc.ID, datetime=datetime)

            if doc.ID in config['match_cache']:
                b.uuid = config['match_cache'][doc.ID][0]
                b.authors = config['match_cache'][doc.ID][1]

            b.device_collections = [get_full_hierarchy(doc.Parent)]
            booklist.add_book(b, replace_metadata=True)

        print('booklist:', booklist)
        return booklist

    def upload_books(self, files, names, on_card=None, end_session=True, metadata=None):
        print('#######' + inspect.currentframe().f_code.co_name)
        print(files)
        print(names)

        ids = list()

        if on_card:
            return ids()

        self.rm_client.renew_token()

        from calibre_plugins.remarkable_cloud_driver.rmapy.document import ZipDocument
        for i, file in enumerate(files):
            if metadata and metadata[i].get('title'):
                display_name = metadata[i].get('title')
            else:
                import os
                display_name = os.path.splitext(os.path.basename(names[i]))[0]

            zip_doc = ZipDocument(doc=file, display_name=display_name)
            # TODO: add errors in case of failure
            r = self.rm_client.upload(zip_doc)

            ids.append(zip_doc.ID)

        return ids

    @classmethod
    def add_books_to_metadata(cls, locations, metadata, booklists):
        print('#######' + inspect.currentframe().f_code.co_name)
        print(locations)
        print(metadata)
        print(booklists)
        for i, rm_id in enumerate(locations):
            metadata[i].set('rm_id', rm_id)
            config['match_cache'][rm_id] = (metadata[i].uuid, metadata[i].authors)

        # TODO: add metadata to booklist

    def delete_books(self, paths, end_session=True):
        print('#######' + inspect.currentframe().f_code.co_name)
        print(paths)
        for rm_id in paths:
            doc_to_delete = self.rm_client.get_doc(rm_id)
            deleted = self.rm_client.delete(doc_to_delete)
            if deleted:
                self.ignore_books.add(rm_id)

    @classmethod
    def remove_books_from_metadata(cls, paths, booklists):
        print('#######' + inspect.currentframe().f_code.co_name)
        print(paths)
        print(booklists)
        # TODO: use a dictionnary for the book for faster lookup ?
        for booklist in booklists:
            for book in booklist:
                if book.rm_id in paths:
                    booklist.remove(book)

    def sync_booklists(self, booklists, end_session=True):
        print('###########"""sync_booklists ')
        print(booklists)
        for booklist in booklists:
            for book in booklist:
                if book.uuid and book.rm_id not in config['match_cache']:
                    config['match_cache'][book.rm_id] = (book.uuid, book.authors)

        # TODO: more readable name for saving config
        dump()

    def get_file(self, path, outfile, end_session=True):
        print('#######' + inspect.currentframe().f_code.co_name)
        print(path)
        print(outfile)
        meta = self.rm_client.get_doc(path)
        book = self.rm_client.download(meta)
        if book.pdf:
            outfile.write(book.pdf.read())
        elif book.epub:
            outfile.write(book.epub.read())

    @classmethod
    def settings(cls):
        opts = super(RemarkableCloudDriver, cls)._config().parse()
        return opts

    def get_device_uid(self):
        print('###########"""get_device_uid ')
        # there is no device per se, soooooo device token as uid ?
        return config['devicetoken']

    def ignore_connected_device(self, uid):
        print('#######' + inspect.currentframe().f_code.co_name)
        pass

    def is_usb_connected(self, devices_on_system, debug=False, only_presence=False):
        return False


from calibre.ebooks.metadata.book.base import Metadata
from calibre.ebooks.metadata import title_sort, author_to_author_sort


class Book(Metadata):

    def __init__(self, title, rm_id, authors=[], size=0, tags=[], other=None, datetime=time.gmtime()):
        super().__init__(title, authors=authors, other=other)  # should pass title and author
        self.rm_id = rm_id
        self.datetime = datetime
        self.size = size
        self.tags = tags
        self.path = rm_id
        self.authors = authors

        self.author_sort = author_to_author_sort(self.authors)

    def __eq__(self, other):
        return self.rm_id == getattr(other, 'rm_id', None)

    @property
    def title_sorter(self):
        ans = getattr(self, 'title_sort', None)
        if not ans or self.is_null('title_sort') or ans == _('Unknown'):
            ans = ''
        return ans or title_sort(self.title or '')
