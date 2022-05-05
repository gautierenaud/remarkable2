#!/usr/bin/env python

__license__ = 'GPL v3'
__copyright__ = '2021, Renaud Tamon Gautier <gautierenaud at gmail.com>'
__docformat__ = 'restructuredtext en'

'''
Driver for remarkable 2 tablets, but using the cloud api provided by remarkable. May work on the first gen as well, but
not tested.
'''

from base64 import decode
import inspect
import logging
import sys
import time
import subprocess
import re

from calibre.devices.usbms.device import Device

logger = logging.getLogger("mechanize")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


class RemarkableSSHDriver(Device):
    name = 'Remarkable 2 SSH Interface'
    gui_name = 'Remarkable 2'
    description = _('Communicate with Remarkable\'s through ssh')
    author = 'Renaud Tamon GAUTIER'
    version = (0, 0, 1)

    # only tested on linux though...
    supported_platforms = ['windows', 'osx', 'linux']

    FORMATS = ['epub', 'pdf']

    MANAGES_DEVICE_PRESENCE = True

    CAN_SET_METADATA = ['title', 'authors', 'collections']

    def __init__(self, args):
        super().__init__(args)
        self.report_progress = lambda x, y: None
        self.rm_client = None
        # the refresh of the device's library after a deletion will be too quick, before the deletion actually takes
        # place. So we have to maintain a list of books to ignore
        self.ignore_books = set()

    def startup(self):
        print('Hello there')

    def detect_managed_devices(self, devices_on_system, force_refresh=False):
        return self

    def debug_managed_device_detection(self, devices_on_system, output):
        return False

    def open(self, connected_device, library_uuid):
        # since it is a connection to a cloud, nothing to be done here
        print('open remarkable device')
        ret = subprocess.run(['ssh', '-o', 'ConnectTimeout=5', '-M', '-S', 'calibre-remarkable-ssh', '-q', '-f', 'root@10.11.99.1', '-N']).returncode
        if ret == 0:
            print('ssh socker is open')
        else:
            raise Exception('ssh connection error')
        # subprocess.run(['ssh', 'root@10.11.99.1', 'ls'])

    def set_progress_reporter(self, report_progress):
        self.report_progress = report_progress

    def get_device_information(self, end_session=True):
        return 'remarkable ssh', '0.0.1', 'whatever', ''

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

        res = subprocess.run(['ssh', '-S', 'calibre-remarkable-ssh', 'root@10.11.99.1', 'find /home/root/.local/share/remarkable/xochitl/ -type f -name "*.metadata" -exec grep -qw "DocumentType" {} \; -exec grep "visibleName" {} \; -print'], capture_output=True)

        raw_output = res.stdout

        decoded = raw_output.decode('utf8').strip().split('\n')
        if not decoded or len(decoded) % 2 != 0:
            print("Wrong entry number: ", len(decoded))
            return booklist
        
        raw_entries = list(zip(decoded[0::2], decoded[1::2]))
        for raw_name, raw_id in raw_entries:
            name_search = re.search('"visibleName": "(.*)"', raw_name)
            name = name_search.group(1)

            id_search = re.search('/home/root/\.local/share/remarkable/xochitl/(.*)\.metadata', raw_id)
            id = id_search.group(1)

            b = Book(title=name, rm_id=id)

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

        # from calibre_plugins.remarkable_cloud_driver.rmapy.document import ZipDocument
        # for i, file in enumerate(files):
        #     if metadata and metadata[i].get('title'):
        #         display_name = metadata[i].get('title')
        #     else:
        #         import os
        #         display_name = os.path.splitext(os.path.basename(names[i]))[0]

        #     zip_doc = ZipDocument(doc=file, display_name=display_name)
        #     # TODO: add errors in case of failure
        #     r = self.rm_client.upload(zip_doc)

        #     ids.append(zip_doc.ID)

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

        # # TODO: more readable name for saving config
        # dump()

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
        opts = super(RemarkableSSHDriver, cls)._config().parse()
        return opts

    def get_device_uid(self):
        print('get_device_uid...')

        res = subprocess.run(['ssh', '-S', 'calibre-remarkable-ssh', 'root@10.11.99.1', 'cat /etc/machine-id'], capture_output=True)
        id = res.stdout.decode('utf-8').strip()
        
        print('id is:', id)

        return id

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
