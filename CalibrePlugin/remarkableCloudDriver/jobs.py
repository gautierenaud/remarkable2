
from calibre.gui2.threaded_jobs import ThreadedJob
from calibre_plugins.remarkable_cloud.rmapy.api import Client

rm_client = Client()


def update_token():
    rm_client.renew_token()


def get_upload_books_job(books, db):
    return ThreadedJob('remarkablecloud', 'Upload files to reMarkable Cloud',
                       upload_books, (books, db), {}, None)


def upload_books(books, db, log=None, abort=None, notifications=True):
    print(f'Uploading {len(books)} books')
    from calibre_plugins.remarkable_cloud.rmapy.document import ZipDocument
    for book_id, fmt in books:
        file_path = db.format_abspath(book_id, fmt)
        zip_doc = ZipDocument(doc=file_path)
        rm_client.upload(zip_doc)
        print(zip_doc.ID)

