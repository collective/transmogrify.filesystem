import os
import mimetypes

from zope.interface import implements, classImplements

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection

from collective.transmogrifier.utils import resolvePackageReference
from collective.transmogrifier.utils import Matcher

from OFS.Image import Image, File

class FilesystemSource(object):
    """Custom section which can read files, folders and and images from the
    filesystem.
    """
    
    implements(ISection)
    classImplements(ISectionBlueprint)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        
        self.directory  = resolvePackageReference(options['directory'])
        self.folderType = options.get('folder-type', 'Folder')
        
        self.fileType   = options.get('file-type', 'File')
        self.imageType  = options.get('image-type', 'Image')
        
        self.fileField  = options.get('file-type', 'file')
        self.imageField = options.get('image-type', 'image')
        
        self.wrapData   = options.get('wrap-data', 'True').lower() == 'true'
        self.defaultMimeType = options.get('default-mime-type', 'application/octet-stream')
        
        ignored = options.get('ignored') or ''
        self.ignored = Matcher(*ignored.splitlines())

    def __iter__(self):
        
        for item in self.previous:
            yield item
        
        for dirpath, dirnames, filenames in os.walk(self.directory):
            
            # Create folders first, if necessary
            for dirname in dirnames:
                dirPath = os.path.join(dirpath, dirname)
                zodbPath = self.getZODBPath(dirPath)
                
                if self.ignored(dirPath)[1]:
                    continue
                
                _type = self.folderType
                
                
                yield {'_type': self.folderType,
                       '_path': zodbPath,
                       }
            
            # Then import files
            for filename in filenames:
                
                filePath = os.path.join(dirpath, filename)
                zodbPath = self.getZODBPath(dirPath)
                
                if self.ignored(filePath)[1]:
                    continue
                
                _type = self.fileType
                fieldname = self.fileField
                mimeType = self.defaultMimeType
                wrapClass = File
                
                # Try to guess mime type and content type
                basename, extension = os.path.splitext(filename)
                if extension and extension.lower() in mimetypes.types_map:
                    mimeType = mimetypes.types_map[extension.lower()]
                    if mimeType.startswith('image'):
                        _type = self.imageType
                        fieldname = self.imageField
                        wrapClass = Image
                        
                infile = open(filePath, 'rb')
                if self.wrapData:
                    fileData = wrapClass(filename, filename, infile, mimeType)
                    fileData.filename = filename
                else:
                    fileData = infile.read()
                infile.close()
                
                yield {'_type': _type,
                        '_path': zodbPath,
                        '_mimetype': mimeType,
                        fieldname: fileData,
                       }
    
    def getZODBPath(self, filePath):
        zodbPath = filePath[len(self.directory):]
        if os.path.sep != '/':
            zodbPath = zodbPath.replace(os.path.sep, '/')
        return zodbPath
