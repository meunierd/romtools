"""
Utils for creating xdelta patches.
"""
import logging
from subprocess import check_output, CalledProcessError
from shutil import copyfile
from os import remove, path


class PatchChecksumError(Exception):
    def __init__(self, message, errors):
        super(PatchChecksumError, self).__init__(message)


class Patch:
    # TODO: Abstract out the need for "edited" by just copying the original
    # file.
    def __init__(self, original, filename, edited=None, xdelta_dir='.'):
        self.original = original
        self.edited = edited
        self.filename = filename

        # self.xdelta_path = path.join(xdelta_dir, 'xdelta3')
        self.xdelta_path = 'xdelta3'

    def create(self):
        if self.edited is None:
            raise Exception
        cmd = '"%s" -f -s "%s" "%s" "%s' % (self.xdelta_path, self.original, self.edited, self.filename)
        print(cmd)
        logging.info(cmd)
        try:
            check_output(cmd)
        except CalledProcessError:
            raise Exception('Something went wrong', [])

    def apply(self):
        if not self.edited:
            copyfile(self.original, self.original + "_temp")
            self.edited = self.original
            self.original = self.original + "_temp"
        cmd = [
            self.xdelta_path,
            '-f',
            '-d',
            '-s',
            self.original,
            self.filename,
            self.edited,
        ]

        logging.info(cmd)
        try:
            check_output(cmd)
        except CalledProcessError:
            raise PatchChecksumError('Target file had incorrect checksum', [])
        finally:
            if self.original.endswith('_temp'):
                remove(self.original)
