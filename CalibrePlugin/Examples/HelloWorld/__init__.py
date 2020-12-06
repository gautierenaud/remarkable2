import os

from calibre.customize import FileTypePlugin


class HelloWorld(FileTypePlugin):
    name = 'Hello World Plugin'
    description = 'Set Publisher to Hello World for all conversions'
    supported_platforms = ['linux']
    author = 'Abcd Efg'
    version = (0, 0, 1)
    file_types = set(['epub', 'mobi'])
    on_postprocess = True
    minimum_calibre_version = (0, 7, 53)

    def run(self, path_to_ebook):
        from calibre.ebooks.metadata.meta import get_metadata, set_metadata
        with open(path_to_ebook, 'r+b') as file:
            ext = os.path.splitext(path_to_ebook)[-1][1:].lower()
            mi = get_metadata(file, ext)
            mi.Publisher = 'Hello World'
            mi.publisher = 'Hello World'
            mi.comments = 'Good fine yes'
            print(mi)
            set_metadata(file, mi, ext)
        return path_to_ebook
