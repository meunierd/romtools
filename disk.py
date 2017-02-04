"""
Utils for extracting and replacing files in disk images.
The standard tool to do this is EditDisk/DiskExplorer, but that has no CLI,
so we have to use a rather obscure Japanese utility called NDC.exe, found here:

http://euee.web.fc2.com/tool/nd.html

"""

import os
# TODO: Use subprocess instead of os.system to check the output and see if it worked.
from shutil import copyfile

NDC_PATH = os.path.abspath(__file__) 

SUPPORTED_FILE_FORMATS = ['fdi', 'hdi', 'hdm', 'flp', 'vmdk', 'dsk', 'vfd', 'vhd',
                          'hdd', 'img', 'd88', 'tfd', 'thd', 'nfd', 'nhd', 'h0', 'h1',
                          'h2', 'h3', 'h4', 'hdm', 'slh']
# (hdm requires conversion to flp, but that conersion gets done below)

def file_to_string(file_path, start=0, length=0):
    # Defaults: read full file from start.
    f = open(file_path, 'rb+')
    f.seek(start)
    if length:
        return f.read(length)
    else:
        return f.read()

class Disk:
    def __init__(self, filename):
        self.filename = filename
        self.extension = filename.split('.')[-1].lower()
        assert self.extension in SUPPORTED_FILE_FORMATS # TODO use an exception

        self.original_extension = self.extension
        self.dir = os.path.abspath(os.path.join(filename, os.pardir))

        if self.extension == 'hdm':
            new_disk_filename = self.filename.split('.')[0] + '.flp'
            copyfile(self.filename, new_disk_filename)
            self.filename = new_disk_filename


    def extract(self, filename, path_in_disk=None):
        # TODO: Add path_in_disk support.

        cmd = 'ndc G "%s" 0 %s .' % (self.filename, filename)
        print cmd
        os.system(cmd)

        return Gamefile(filename, self)

    def delete(self, filename, path_in_disk=None):
        del_cmd = 'ndc D "%s" 0' % (self.filename)
        if path_in_disk:
            del_cmd += ' ' + os.path.join(path_in_disk, filename)
        else:
            del_cmd += ' ' + filename
        os.system(del_cmd)

    def insert(self, filename, path_in_disk=None):
        # First, delete the original file in the disk if applicable.
        # (TODO: this may not be necessary?? check it agian)
        self.delete(filename, path_in_disk)

        cmd = 'ndc P "%s" 0 %s' % (self.filename, filename)
        if path_in_disk:
            cmd += ' ' + path_in_disk
        os.system(cmd)

        if self.original_extension == 'hdm':
            original_disk_filename = self.filename.split('.')[0] + '.hdm'
            copyfile(self.filename, original_disk_filename)

    def __repr__(self):
        return self.filename

class Gamefile(object):
    def __init__(self, filename, disk, dest_disk=None, pointer_constant=None):
        self.filename = filename
        self.disk = disk
        self.dest_disk = dest_disk

        self.original_filestring = file_to_string(filename)
        self.filestring = "" + self.original_filestring

        self.pointer_constant = pointer_constant

    #def incorporate(self):
    #    """Add the edited file to the Disk in the original's place."""
    #    for b in self.blocks:
    #        b.incorporate()

    def write(self):
        """Write the new data to an independent file for later inspection."""
        dest_path = os.path.join(self.dest_disk.dir, self.filename)

        with open(dest_path, 'wb') as fileopen:
            fileopen.write(self.filestring)

        self.dest_disk.insert(self.filename)


    def __repr__(self):
        return self.filename

class Block(object):
    """A text block.

    Attributes:
        gamefile: The EXEFile or DATFile object it belongs to.
        start = Beginning offset of the block.
        stop  = Ending offset of the block.
        original_blockstring: Hex string of entire block.
        blockstring: Hex string of entire block for editing.
        translations: List of Translation objects.
        """

    def __init__(self, gamefile, (start, stop)):
        self.gamefile = gamefile
        self.start = start
        self.stop = stop

        self.original_blockstring = file_to_string(self.gamefile.disk.filename)
        self.blockstring = "" + self.original_blockstring

    def __repr__(self):
        return "%s (%s, %s)" % (self.gamefile, hex(self.start), hex(self.stop))


if __name__ == '__main__':
    #EVODisk = Disk('46OM.hdi')
    #EVODisk.insert('windhex.cfg')

    EVOHDM = Disk('EVO.hdm')
    EVOHDM.insert('AV300.GDT')
    EVOHDM.extract('AV300.GDT')

