import os
import unittest
from transmogrify.filesystem.source import FilesystemSource


class FilesystemSourceTest(unittest.TestCase):

    def _makeOne(self, transmogrifier={}, name='test', previous=(), **options):
        return FilesystemSource(transmogrifier, name, options, previous)
    
    def test_plain_filename(self):
        """Test that also plain filenames can be passed as directory. """
        source = self._makeOne(directory=os.getcwd())
        self.assertEquals([], list(source))

    def test_empty_directory(self):
        source = self._makeOne(directory='transmogrify.filesystem.tests:empty',
                                ignored='re:.*\.svn.*\nre:.*\.DS_Store\n')
        self.assertEquals([], list(source))
    
    def test_directory_not_found(self):
        source = self._makeOne(directory='transmogrify.filesystem.tests:invalid')
        self.assertRaises(ValueError, list, source)
    
    def test_metadata_required_not_given(self):
        options = {'require-metadata': 'true',
                   'directory': 'transmogrify.filesystem.tests:empty'}
        source = self._makeOne(**options)
        self.assertRaises(ValueError, list, source)
    
    def test_metadata_required_not_found(self):
        options = {'require-metadata': 'true',
                   'metadata': 'transmogrify.filesystem.tests:invalid.csv',
                   'directory': 'transmogrify.filesystem.tests:empty'}
        source = self._makeOne(**options)
        self.assertRaises(IOError, list, source)
    
    def test_metadata_required_empty(self):
        options = {'require-metadata': 'true',
                   'metadata': 'transmogrify.filesystem.tests:empty.csv',
                   'directory': 'transmogrify.filesystem.tests:empty'}
        source = self._makeOne(**options)
        self.assertRaises(ValueError, list, source)
    
    def test_metadata_no_path(self):
        options = {'require-metadata': 'true',
                   'metadata': 'transmogrify.filesystem.tests:nopath.csv',
                   'directory': 'transmogrify.filesystem.tests:empty'}
        source = self._makeOne(**options)
        self.assertRaises(ValueError, list, source)

    def test_metadata_bad_delimiter(self):
        options = {'require-metadata': 'true',
                   'metadata':  'transmogrify.filesystem.tests:metadata/delimiter.csv',
                   'directory': 'transmogrify.filesystem.tests:metadata',
                   'delimiter': ',',}
        source = self._makeOne(**options)
        self.assertRaises(ValueError, list, source)

    def test_metadata_strict_error(self):
        options = {'require-metadata': 'true',
                   'metadata':  'transmogrify.filesystem.tests:metadata/delimiter.csv',
                   'directory': 'transmogrify.filesystem.tests:metadata',
                   'delimiter': '|',
                   'strict':    'True'}
        source = self._makeOne(**options)
        self.assertRaises(ValueError, list, source)
        
    def test_normal(self):
        source = self._makeOne(directory='transmogrify.filesystem.tests:data',
                               ignored='re:.*\.svn.*\nre:.*\.DS_Store\n')
        results = list(source)
        self.assertEquals(6, len(results))
        
        # Folders at each level come first
        self.assertEquals({'_path': '/subdir', '_type': 'Folder'}, results[0])
        
        # Then files, in filename order
        self.assertEquals('image/jpeg',                  results[1]['_mimetype'])
        self.assertEquals('/logo.jpg',                   results[1]['_path'])
        self.assertEquals('Image',                       results[1]['_type'])
        self.assertEquals('logo.jpg',                    results[1]['image'].filename)
        self.assertEquals('logo.jpg',                    results[1]['image'].id())
        self.assertEquals('image/jpeg',                  results[1]['image'].content_type)
                                                         
        self.assertEquals('application/octet-stream',    results[2]['_mimetype'])
        self.assertEquals('/noextension',                results[2]['_path'])
        self.assertEquals('File',                        results[2]['_type'])
        self.assertEquals('noextension',                 results[2]['file'].filename)
        self.assertEquals('noextension',                 results[2]['file'].id())
        self.assertEquals('application/octet-stream',    results[2]['file'].content_type)
                                                         
        self.assertEquals('text/plain',                  results[3]['_mimetype'])
        self.assertEquals('/textfile.txt',               results[3]['_path'])
        self.assertEquals('File',                        results[3]['_type'])
        self.assertEquals('textfile.txt',                results[3]['file'].filename)
        self.assertEquals('textfile.txt',                results[3]['file'].id())
        self.assertEquals('text/plain',                  results[3]['file'].content_type)
        
        # Then the next level of folders
        self.assertEquals({'_path': '/subdir/subsubdir', '_type': 'Folder'}, results[4])
        
        # Then files
        self.assertEquals('text/plain',                  results[5]['_mimetype'])
        self.assertEquals('/subdir/subsubdir/other.txt', results[5]['_path'])
        self.assertEquals('File',                        results[5]['_type'])
        self.assertEquals('other.txt',                   results[5]['file'].filename)
        self.assertEquals('other.txt',                   results[5]['file'].id())
        self.assertEquals('text/plain',                  results[5]['file'].content_type)
    
    def test_ignore(self):
        source = self._makeOne(directory='transmogrify.filesystem.tests:data',
                               ignored='re:.*\.svn.*\nre:.*\.DS_Store\n/logo.jpg\nre:.*\.txt')
        
        results = list(source)
        self.assertEquals(3, len(results))
        
        # Folders at each level come first
        self.assertEquals({'_path': '/subdir', '_type': 'Folder'}, results[0])
        
        self.assertEquals('application/octet-stream',    results[1]['_mimetype'])
        self.assertEquals('/noextension',                results[1]['_path'])
        self.assertEquals('File',                        results[1]['_type'])
        self.assertEquals('noextension',                 results[1]['file'].filename)
        self.assertEquals('noextension',                 results[1]['file'].id())
        self.assertEquals('application/octet-stream',    results[1]['file'].content_type)
                                                         
        # Then the next level of folders
        self.assertEquals({'_path': '/subdir/subsubdir', '_type': 'Folder'}, results[2])
            
    def test_folder_type(self):
        options = {'directory':   'transmogrify.filesystem.tests:data',
                   'ignored':     're:.*\.svn.*\nre:.*\.DS_Store\n',
                   'folder-type': 'My Folder'}
        source = self._makeOne(**options)
        results = list(source)
        self.assertEquals(6, len(results))
        
        # Folders at each level come first
        self.assertEquals({'_path': '/subdir', '_type': 'My Folder'}, results[0])
        
        # Then files, in filename order
        self.assertEquals('image/jpeg',                  results[1]['_mimetype'])
        self.assertEquals('/logo.jpg',                   results[1]['_path'])
        self.assertEquals('Image',                       results[1]['_type'])
        self.assertEquals('logo.jpg',                    results[1]['image'].filename)
        self.assertEquals('logo.jpg',                    results[1]['image'].id())
        self.assertEquals('image/jpeg',                  results[1]['image'].content_type)
                                                         
        self.assertEquals('application/octet-stream',    results[2]['_mimetype'])
        self.assertEquals('/noextension',                results[2]['_path'])
        self.assertEquals('File',                        results[2]['_type'])
        self.assertEquals('noextension',                 results[2]['file'].filename)
        self.assertEquals('noextension',                 results[2]['file'].id())
        self.assertEquals('application/octet-stream',    results[2]['file'].content_type)
                                                         
        self.assertEquals('text/plain',                  results[3]['_mimetype'])
        self.assertEquals('/textfile.txt',               results[3]['_path'])
        self.assertEquals('File',                        results[3]['_type'])
        self.assertEquals('textfile.txt',                results[3]['file'].filename)
        self.assertEquals('textfile.txt',                results[3]['file'].id())
        self.assertEquals('text/plain',                  results[3]['file'].content_type)
        
        # Then the next level of folders
        self.assertEquals({'_path': '/subdir/subsubdir', '_type': 'My Folder'}, results[4])
        
        # Then files
        self.assertEquals('text/plain',                  results[5]['_mimetype'])
        self.assertEquals('/subdir/subsubdir/other.txt', results[5]['_path'])
        self.assertEquals('File',                        results[5]['_type'])
        self.assertEquals('other.txt',                   results[5]['file'].filename)
        self.assertEquals('other.txt',                   results[5]['file'].id())
        self.assertEquals('text/plain',                  results[5]['file'].content_type)
    
    def test_image_type(self):
        options = {'directory':   'transmogrify.filesystem.tests:data',
                   'ignored':     're:.*\.svn.*\nre:.*\.DS_Store\n',
                   'image-type':  'My Image'}
        source = self._makeOne(**options)
        results = list(source)
        self.assertEquals(6, len(results))
        
        # Folders at each level come first
        self.assertEquals({'_path': '/subdir', '_type': 'Folder'}, results[0])
        
        # Then files, in filename order
        self.assertEquals('image/jpeg',                  results[1]['_mimetype'])
        self.assertEquals('/logo.jpg',                   results[1]['_path'])
        self.assertEquals('My Image',                    results[1]['_type'])
        self.assertEquals('logo.jpg',                    results[1]['image'].filename)
        self.assertEquals('logo.jpg',                    results[1]['image'].id())
        self.assertEquals('image/jpeg',                  results[1]['image'].content_type)
                                                         
        self.assertEquals('application/octet-stream',    results[2]['_mimetype'])
        self.assertEquals('/noextension',                results[2]['_path'])
        self.assertEquals('File',                        results[2]['_type'])
        self.assertEquals('noextension',                 results[2]['file'].filename)
        self.assertEquals('noextension',                 results[2]['file'].id())
        self.assertEquals('application/octet-stream',    results[2]['file'].content_type)
                                                         
        self.assertEquals('text/plain',                  results[3]['_mimetype'])
        self.assertEquals('/textfile.txt',               results[3]['_path'])
        self.assertEquals('File',                        results[3]['_type'])
        self.assertEquals('textfile.txt',                results[3]['file'].filename)
        self.assertEquals('textfile.txt',                results[3]['file'].id())
        self.assertEquals('text/plain',                  results[3]['file'].content_type)
        
        # Then the next level of folders
        self.assertEquals({'_path': '/subdir/subsubdir', '_type': 'Folder'}, results[4])
        
        # Then files
        self.assertEquals('text/plain',                  results[5]['_mimetype'])
        self.assertEquals('/subdir/subsubdir/other.txt', results[5]['_path'])
        self.assertEquals('File',                        results[5]['_type'])
        self.assertEquals('other.txt',                   results[5]['file'].filename)
        self.assertEquals('other.txt',                   results[5]['file'].id())
        self.assertEquals('text/plain',                  results[5]['file'].content_type)
    
    def test_file_type(self):
        options = {'directory':   'transmogrify.filesystem.tests:data',
                   'ignored':     're:.*\.svn.*\nre:.*\.DS_Store\n',
                   'file-type':   'My File'}
        source = self._makeOne(**options)
        results = list(source)
        self.assertEquals(6, len(results))
        
        # Folders at each level come first
        self.assertEquals({'_path': '/subdir', '_type': 'Folder'}, results[0])
        
        # Then files, in filename order
        self.assertEquals('image/jpeg',                  results[1]['_mimetype'])
        self.assertEquals('/logo.jpg',                   results[1]['_path'])
        self.assertEquals('Image',                       results[1]['_type'])
        self.assertEquals('logo.jpg',                    results[1]['image'].filename)
        self.assertEquals('logo.jpg',                    results[1]['image'].id())
        self.assertEquals('image/jpeg',                  results[1]['image'].content_type)
                                                         
        self.assertEquals('application/octet-stream',    results[2]['_mimetype'])
        self.assertEquals('/noextension',                results[2]['_path'])
        self.assertEquals('My File',                     results[2]['_type'])
        self.assertEquals('noextension',                 results[2]['file'].filename)
        self.assertEquals('noextension',                 results[2]['file'].id())
        self.assertEquals('application/octet-stream',    results[2]['file'].content_type)
                                                         
        self.assertEquals('text/plain',                  results[3]['_mimetype'])
        self.assertEquals('/textfile.txt',               results[3]['_path'])
        self.assertEquals('My File',                     results[3]['_type'])
        self.assertEquals('textfile.txt',                results[3]['file'].filename)
        self.assertEquals('textfile.txt',                results[3]['file'].id())
        self.assertEquals('text/plain',                  results[3]['file'].content_type)
        
        # Then the next level of folders
        self.assertEquals({'_path': '/subdir/subsubdir', '_type': 'Folder'}, results[4])
        
        # Then files
        self.assertEquals('text/plain',                  results[5]['_mimetype'])
        self.assertEquals('/subdir/subsubdir/other.txt', results[5]['_path'])
        self.assertEquals('My File',                     results[5]['_type'])
        self.assertEquals('other.txt',                   results[5]['file'].filename)
        self.assertEquals('other.txt',                   results[5]['file'].id())
        self.assertEquals('text/plain',                  results[5]['file'].content_type)
        
    def test_image_field(self):
        options = {'directory':   'transmogrify.filesystem.tests:data',
                   'ignored':     're:.*\.svn.*\nre:.*\.DS_Store\n',
                   'image-field': 'aimage'}
        source = self._makeOne(**options)
        results = list(source)
        self.assertEquals(6, len(results))
        
        # Folders at each level come first
        self.assertEquals({'_path': '/subdir', '_type': 'Folder'}, results[0])
        
        # Then files, in filename order
        self.assertEquals('image/jpeg',                  results[1]['_mimetype'])
        self.assertEquals('/logo.jpg',                   results[1]['_path'])
        self.assertEquals('Image',                       results[1]['_type'])
        self.assertEquals('logo.jpg',                    results[1]['aimage'].filename)
        self.assertEquals('logo.jpg',                    results[1]['aimage'].id())
        self.assertEquals('image/jpeg',                  results[1]['aimage'].content_type)
                                                         
        self.assertEquals('application/octet-stream',    results[2]['_mimetype'])
        self.assertEquals('/noextension',                results[2]['_path'])
        self.assertEquals('File',                        results[2]['_type'])
        self.assertEquals('noextension',                 results[2]['file'].filename)
        self.assertEquals('noextension',                 results[2]['file'].id())
        self.assertEquals('application/octet-stream',    results[2]['file'].content_type)
                                                         
        self.assertEquals('text/plain',                  results[3]['_mimetype'])
        self.assertEquals('/textfile.txt',               results[3]['_path'])
        self.assertEquals('File',                        results[3]['_type'])
        self.assertEquals('textfile.txt',                results[3]['file'].filename)
        self.assertEquals('textfile.txt',                results[3]['file'].id())
        self.assertEquals('text/plain',                  results[3]['file'].content_type)
        
        # Then the next level of folders
        self.assertEquals({'_path': '/subdir/subsubdir', '_type': 'Folder'}, results[4])
        
        # Then files
        self.assertEquals('text/plain',                  results[5]['_mimetype'])
        self.assertEquals('/subdir/subsubdir/other.txt', results[5]['_path'])
        self.assertEquals('File',                        results[5]['_type'])
        self.assertEquals('other.txt',                   results[5]['file'].filename)
        self.assertEquals('other.txt',                   results[5]['file'].id())
        self.assertEquals('text/plain',                  results[5]['file'].content_type)
    
    def test_file_field(self):
        options = {'directory':   'transmogrify.filesystem.tests:data',
                   'ignored':     're:.*\.svn.*\nre:.*\.DS_Store\n',
                   'file-field':  'afile'}
        source = self._makeOne(**options)
        results = list(source)
        self.assertEquals(6, len(results))
        
        # Folders at each level come first
        self.assertEquals({'_path': '/subdir', '_type': 'Folder'}, results[0])
        
        # Then files, in filename order
        self.assertEquals('image/jpeg',                  results[1]['_mimetype'])
        self.assertEquals('/logo.jpg',                   results[1]['_path'])
        self.assertEquals('Image',                       results[1]['_type'])
        self.assertEquals('logo.jpg',                    results[1]['image'].filename)
        self.assertEquals('logo.jpg',                    results[1]['image'].id())
        self.assertEquals('image/jpeg',                  results[1]['image'].content_type)
                                                         
        self.assertEquals('application/octet-stream',    results[2]['_mimetype'])
        self.assertEquals('/noextension',                results[2]['_path'])
        self.assertEquals('File',                        results[2]['_type'])
        self.assertEquals('noextension',                 results[2]['afile'].filename)
        self.assertEquals('noextension',                 results[2]['afile'].id())
        self.assertEquals('application/octet-stream',    results[2]['afile'].content_type)
                                                         
        self.assertEquals('text/plain',                  results[3]['_mimetype'])
        self.assertEquals('/textfile.txt',               results[3]['_path'])
        self.assertEquals('File',                        results[3]['_type'])
        self.assertEquals('textfile.txt',                results[3]['afile'].filename)
        self.assertEquals('textfile.txt',                results[3]['afile'].id())
        self.assertEquals('text/plain',                  results[3]['afile'].content_type)
        
        # Then the next level of folders
        self.assertEquals({'_path': '/subdir/subsubdir', '_type': 'Folder'}, results[4])
        
        # Then files
        self.assertEquals('text/plain',                  results[5]['_mimetype'])
        self.assertEquals('/subdir/subsubdir/other.txt', results[5]['_path'])
        self.assertEquals('File',                        results[5]['_type'])
        self.assertEquals('other.txt',                   results[5]['afile'].filename)
        self.assertEquals('other.txt',                   results[5]['afile'].id())
        self.assertEquals('text/plain',                  results[5]['afile'].content_type)
    
    def test_unwrapped(self):
        options = {'directory':   'transmogrify.filesystem.tests:data',
                   'ignored':     're:.*\.svn.*\nre:.*\.DS_Store\n',
                   'wrap-data':   'false'}
        source = self._makeOne(**options)
        results = list(source)
        self.assertEquals(6, len(results))
        
        # Folders at each level come first
        self.assertEquals({'_path': '/subdir', '_type': 'Folder'}, results[0])
        
        # Then files, in filename order
        self.assertEquals('image/jpeg',                  results[1]['_mimetype'])
        self.assertEquals('/logo.jpg',                   results[1]['_path'])
        self.assertEquals('Image',                       results[1]['_type'])
        self.assertEquals(5156,                          len(results[1]['image']))
        
        self.assertEquals('application/octet-stream',    results[2]['_mimetype'])
        self.assertEquals('/noextension',                results[2]['_path'])
        self.assertEquals('File',                        results[2]['_type'])
        self.assertEquals('This file has no extension.', results[2]['file'])
                                                         
        self.assertEquals('text/plain',                  results[3]['_mimetype'])
        self.assertEquals('/textfile.txt',               results[3]['_path'])
        self.assertEquals('File',                        results[3]['_type'])
        self.assertEquals('Sample text file',            results[3]['file'])
        
        # Then the next level of folders
        self.assertEquals({'_path': '/subdir/subsubdir', '_type': 'Folder'}, results[4])
        
        # Then files
        self.assertEquals('text/plain',                  results[5]['_mimetype'])
        self.assertEquals('/subdir/subsubdir/other.txt', results[5]['_path'])
        self.assertEquals('File',                        results[5]['_type'])
        self.assertEquals('Another text file',           results[5]['file'])
    
    def test_default_mime_type(self):
        options = {'directory': 'transmogrify.filesystem.tests:data',
                   'ignored': 're:.*\.svn.*\nre:.*\.DS_Store\n',
                    'default-mime-type': 'text/plain',
                  }
                    
        source = self._makeOne(**options)
        results = list(source)
        self.assertEquals(6, len(results))
        
        # Folders at each level come first
        self.assertEquals({'_path': '/subdir', '_type': 'Folder'}, results[0])
        
        # Then files, in filename order
        self.assertEquals('image/jpeg',                  results[1]['_mimetype'])
        self.assertEquals('/logo.jpg',                   results[1]['_path'])
        self.assertEquals('Image',                       results[1]['_type'])
        self.assertEquals('logo.jpg',                    results[1]['image'].filename)
        self.assertEquals('logo.jpg',                    results[1]['image'].id())
        self.assertEquals('image/jpeg',                  results[1]['image'].content_type)
                                                         
        self.assertEquals('text/plain',                  results[2]['_mimetype'])
        self.assertEquals('/noextension',                results[2]['_path'])
        self.assertEquals('File',                        results[2]['_type'])
        self.assertEquals('noextension',                 results[2]['file'].filename)
        self.assertEquals('noextension',                 results[2]['file'].id())
        self.assertEquals('text/plain',                  results[2]['file'].content_type)
                                                         
        self.assertEquals('text/plain',                  results[3]['_mimetype'])
        self.assertEquals('/textfile.txt',               results[3]['_path'])
        self.assertEquals('File',                        results[3]['_type'])
        self.assertEquals('textfile.txt',                results[3]['file'].filename)
        self.assertEquals('textfile.txt',                results[3]['file'].id())
        self.assertEquals('text/plain',                  results[3]['file'].content_type)
        
        # Then the next level of folders
        self.assertEquals({'_path': '/subdir/subsubdir', '_type': 'Folder'}, results[4])
        
        # Then files
        self.assertEquals('text/plain',                  results[5]['_mimetype'])
        self.assertEquals('/subdir/subsubdir/other.txt', results[5]['_path'])
        self.assertEquals('File',                        results[5]['_type'])
        self.assertEquals('other.txt',                   results[5]['file'].filename)
        self.assertEquals('other.txt',                   results[5]['file'].id())
        self.assertEquals('text/plain',                  results[5]['file'].content_type)
    
    def test_metadata_partial(self):
        options = {'directory': 'transmogrify.filesystem.tests:metadata',
                   'metadata':  'transmogrify.filesystem.tests:metadata/metadata.csv',
                   'ignored': 're:.*\.svn.*\nre:.*\.DS_Store\n',
                  }
                    
        source = self._makeOne(**options)
        results = list(source)

        self.assertEquals(7, len(results))
        
        # Folders at each level come first
        self.assertEquals({'_path': '/subdir', '_type': 'Folder',
                           'title': 'Subdir', 'description': 'Subdir description'}, results[0])
                           
        # No metadata for this item
        self.assertEquals({'_path': '/subdir2', '_type': 'Folder'}, results[1])
        
        # file number #3 is delimiter.csv
        
        # Then files, in filename order
        self.assertEquals('text/plain',                  results[3]['_mimetype'])
        self.assertEquals('/file1.txt',                  results[3]['_path'])
        self.assertEquals('File',                        results[3]['_type'])
        self.assertEquals('file1.txt',                   results[3]['file'].filename)
        self.assertEquals('file1.txt',                   results[3]['file'].id())
        self.assertEquals('text/plain',                  results[3]['file'].content_type)
        self.assertEquals('File 1',                      results[3]['title'])
        self.assertEquals('File 1 description',          results[3]['description'])
        
        self.assertEquals('text/plain',                  results[5]['_mimetype'])
        self.assertEquals('/subdir/file2.txt',           results[5]['_path'])
        self.assertEquals('File',                        results[5]['_type'])
        self.assertEquals('file2.txt',                   results[5]['file'].filename)
        self.assertEquals('file2.txt',                   results[5]['file'].id())
        self.assertEquals('text/plain',                  results[5]['file'].content_type)
        self.assertEquals('File 2',                      results[5]['title'])
        self.assertEquals('File 2 description',          results[5]['description'])
        
        # No metadata here either
        self.assertEquals('text/plain',                  results[6]['_mimetype'])
        self.assertEquals('/subdir/file3.txt',           results[6]['_path'])
        self.assertEquals('File',                        results[6]['_type'])
        self.assertEquals('file3.txt',                   results[6]['file'].filename)
        self.assertEquals('file3.txt',                   results[6]['file'].id())
        self.assertEquals('text/plain',                  results[6]['file'].content_type)
        self.assertEquals(None,                          results[6].get('title', None))
        self.assertEquals(None,                          results[6].get('description', None))
        
        # NOTE: metadata.csv file is implicitly excluded
        
    def test_metadata_required(self):
        options = {'directory': 'transmogrify.filesystem.tests:metadata',
                   'metadata':  'transmogrify.filesystem.tests:metadata/metadata.csv',
                   'ignored': 're:.*\.svn.*\nre:.*\.DS_Store\n',
                   'require-metadata': 'true',
                  }
                    
        source = self._makeOne(**options)
        results = list(source)
        self.assertEquals(4, len(results))
        
        # Folders at each level come first
        self.assertEquals({'_path': '/subdir', '_type': 'Folder',
                           'title': 'Subdir', 'description': 'Subdir description'}, results[0])
        
        # No metadata for this item, but folders are always included
        self.assertEquals({'_path': '/subdir2', '_type': 'Folder'}, results[1])
        
        # Then files, in filename order
        self.assertEquals('text/plain',                  results[2]['_mimetype'])
        self.assertEquals('/file1.txt',                  results[2]['_path'])
        self.assertEquals('File',                        results[2]['_type'])
        self.assertEquals('file1.txt',                   results[2]['file'].filename)
        self.assertEquals('file1.txt',                   results[2]['file'].id())
        self.assertEquals('text/plain',                  results[2]['file'].content_type)
        self.assertEquals('File 1',                      results[2]['title'])
        self.assertEquals('File 1 description',          results[2]['description'])
        
        self.assertEquals('text/plain',                  results[3]['_mimetype'])
        self.assertEquals('/subdir/file2.txt',           results[3]['_path'])
        self.assertEquals('File',                        results[3]['_type'])
        self.assertEquals('file2.txt',                   results[3]['file'].filename)
        self.assertEquals('file2.txt',                   results[3]['file'].id())
        self.assertEquals('text/plain',                  results[3]['file'].content_type)
        self.assertEquals('File 2',                      results[3]['title'])
        self.assertEquals('File 2 description',          results[3]['description'])
        
        # Note: items without metadata were ignored

    def test_metadata_custom_delimiter(self):
        options = {'directory': 'transmogrify.filesystem.tests:metadata',
                   'metadata':  'transmogrify.filesystem.tests:metadata/delimiter.csv',
                   'ignored': 're:.*\.svn.*\nre:.*\.DS_Store\n',
                   'require-metadata': 'true',
                   'delimiter': '|',
                  }
                    
        source = self._makeOne(**options)
        results = list(source)
        self.assertEquals(3, len(results))
                
        # Parsed file
        self.assertEquals('text/plain',                  results[2]['_mimetype'])
        self.assertEquals('/file1.txt',                  results[2]['_path'])
        self.assertEquals('File',                        results[2]['_type'])
        self.assertEquals('file1.txt',                   results[2]['file'].filename)
        self.assertEquals('file1.txt',                   results[2]['file'].id())
        self.assertEquals('text/plain',                  results[2]['file'].content_type)
        self.assertEquals('File 1',                      results[2]['title'])
        self.assertEquals('File 1 description',          results[2]['description'])
                
        # Note: items without metadata were ignored

    def test_metadata_strict(self):
        options = {'directory': 'transmogrify.filesystem.tests:metadata',
                   'metadata':  'transmogrify.filesystem.tests:metadata/metadata.csv',
                   'ignored': 're:.*\.svn.*\nre:.*\.DS_Store\n',
                   'require-metadata': 'true',
                   'strict': 'True',
                  }
                    
        source = self._makeOne(**options)
        results = list(source)
        self.assertEquals(4, len(results))
                
        # Parsed file
        self.assertEquals('text/plain',                  results[2]['_mimetype'])
        self.assertEquals('/file1.txt',                  results[2]['_path'])
        self.assertEquals('File',                        results[2]['_type'])
        self.assertEquals('file1.txt',                   results[2]['file'].filename)
        self.assertEquals('file1.txt',                   results[2]['file'].id())
        self.assertEquals('text/plain',                  results[2]['file'].content_type)
        self.assertEquals('File 1',                      results[2]['title'])
        self.assertEquals('File 1 description',          results[2]['description'])
                
        # Note: items without metadata were ignored

    def test_metadata_portal_type(self):
        options = {'directory': 'transmogrify.filesystem.tests:metadata',
                   'metadata':  'transmogrify.filesystem.tests:metadata/portal_type.csv',
                   'ignored': 're:.*\.svn.*\nre:.*\.DS_Store\n',
                   'require-metadata': 'true',
                  }
                    
        source = self._makeOne(**options)
        results = list(source)

        self.assertEquals(3, len(results))
                
        # Parsed file
        self.assertEquals('text/html',                  results[2]['_mimetype'])
        self.assertEquals('/file1.txt',                 results[2]['_path'])
        self.assertEquals('News Item',                  results[2]['_type'])
     
        # Note: items without metadata were ignored           

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
