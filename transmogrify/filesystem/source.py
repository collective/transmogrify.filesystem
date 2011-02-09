import os
import os.path
import csv
import mimetypes

from zope.interface import implements, classProvides

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection

from collective.transmogrifier.utils import resolvePackageReferenceOrFile
from collective.transmogrifier.utils import Matcher

from OFS.Image import File

class FilesystemSource(object):
    """Custom section which can read files, folders and and images from the
    filesystem.
    """
    
    implements(ISection)
    classProvides(ISectionBlueprint)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        
        self.directory  = resolvePackageReferenceOrFile(options['directory'])
        self.metadata   = None
        self.delimiter = None
        self.strict = False
        
        if 'metadata' in options:
            self.metadata = resolvePackageReferenceOrFile(options['metadata'])
            self.delimiter = options.get('delimiter', ',')
            self.strict = options.get('strict', False)
        
        self.requireMetadata = options.get('require-metadata', 'false').lower() != 'false'
        
        self.folderType = options.get('folder-type', 'Folder')
        
        self.fileType   = options.get('file-type', 'File')
        self.imageType  = options.get('image-type', 'Image')
        
        self.fileField  = options.get('file-field', 'file')
        self.imageField = options.get('image-field', 'image')
        
        self.wrapData   = options.get('wrap-data', 'true').lower() == 'true'
        self.defaultMimeType = options.get('default-mime-type', 'application/octet-stream')
        
        ignored = options.get('ignored') or ''
        self.ignored = Matcher(*ignored.splitlines())

    def __iter__(self):
        
        for item in self.previous:
            yield item
        
        metadata = {}
        
        if self.metadata:
            metadataFile = open(self.metadata, 'rb')
            reader = csv.DictReader(metadataFile, delimiter=self.delimiter)

            if reader.fieldnames is None:
                raise ValueError("Metadata CSV is empty.")
            if len(reader.fieldnames) is 1 and self.delimiter not in reader.fieldnames[0]:
                raise ValueError("Metadata CSV does not use the specified delimiter: %s" %(self.delimiter))
            if 'path' not in reader.fieldnames:
                raise ValueError("Metadata CSV file does not have a 'path' column.")

            if self.strict:
                field_count = len(reader.fieldnames)
            
            for row in reader:
                
                if self.strict and field_count != len(row):
                    raise ValueError("Found a row in Metadata CSV that has a different count of fields \
                        compared to first row: %s" %(row))
                
                path = row['path']
                data = row.copy()
                del data['path']
                metadata[path] = data
        
        if self.requireMetadata and not metadata:
            raise ValueError("Metadata is required, but metadata file %s not given or empty" % self.metadata)
        
        if not os.path.exists(self.directory):
            raise ValueError("Directory %s does not exist" % self.directory)

        for dirpath, dirnames, filenames in os.walk(self.directory):
            
            # Create folders first, if necessary
            for dirname in dirnames:
                dirPath = os.path.join(dirpath, dirname)
                zodbPath = self.getZODBPath(dirPath)
                
                if self.ignored(zodbPath)[1]:
                    continue
                
                _type = self.folderType
                
                item = {'_type': self.folderType,
                        '_path': zodbPath}
                
                if zodbPath in metadata:
                    item.update(metadata[zodbPath])
                
                yield item
            
            # Then import files
            for filename in filenames:
                filePath = os.path.join(dirpath, filename)
                zodbPath = self.getZODBPath(filePath)
                
                if self.ignored(zodbPath)[1]:
                    continue
                
                if self.metadata and os.path.abspath(filePath) == os.path.abspath(self.metadata):
                    continue
                
                if self.requireMetadata and zodbPath not in metadata:
                    continue

                if zodbPath in metadata and 'portal_type' in metadata[zodbPath] and \
                   metadata[zodbPath]['portal_type'] in ['News Item', 'Document', 'Event']:
                    # if portal_type is given in metadata.csv, use it!
                    _type = metadata[zodbPath]['portal_type']
                    mimeType = 'text/html'
                    fieldname = 'text'
                    self.wrapData = False
                else:                
                    # else make it File or Image
                    _type = self.fileType
                    fieldname = self.fileField  
                    mimeType = self.defaultMimeType
                                  
                    # Try to guess mime type and content type
                    basename, extension = os.path.splitext(filename)
                    if extension and extension.lower() in mimetypes.types_map:
                        mimeType = mimetypes.types_map[extension.lower()]
                        if mimeType.startswith('image'):
                            _type = self.imageType
                            fieldname = self.imageField
                        
                # read in main content of this item        
                infile = open(filePath, 'rb')
                if self.wrapData:
                    fileData = File(filename, filename, infile, mimeType)
                    fileData.filename = filename
                else:
                    fileData = infile.read()
                infile.close()
                
                item = {'_type': _type,
                        '_path': zodbPath,
                        '_mimetype': mimeType,
                        fieldname: fileData}
                
                if zodbPath in metadata:
                    item.update(metadata[zodbPath])
                
                yield item
    
    def getZODBPath(self, filePath):
        zodbPath = filePath[len(self.directory):]
        if os.path.sep != '/':
            zodbPath = zodbPath.replace(os.path.sep, '/')
        return zodbPath
