
from calibre.gui2.threaded_jobs import ThreadedJob
from calibre_plugins.remarkable_cloud.rmapy.api import Client

rm_client = Client()


def update_token():
    rm_client.renew_token()


def upload_book(self, book_id, fmt, db):
    job = ThreadedJob('remarkablecloud', 'Upload files to reMarkable Cloud',
                      upload_book_job, (book_id, fmt, db), {}, None)
    self.gui.job_manager.run_threaded_job(job)


def upload_book_job(book_id, fmt, db, log=None, abort=None, notifications=True):
    print(f'starting upload_book job for: {book_id}')
    from calibre_plugins.remarkable_cloud.rmapy.document import ZipDocument
    file_path = db.format_abspath(book_id, fmt)
    zip_doc = ZipDocument(doc=file_path)
    res = rm_client.upload(zip_doc)
