transmogrify.filesystem
=======================

Transmogrifier source for reading files from the filesystem

This package provides a `Transmogrifier
<http://pypi.python.org/pypi/collective.transmogrifier>`_ data source for
reading files, images and directories from the filesystem. The output format
is geared towards constructing Plone ``File``, ``Image`` or ``Folder``
content. It is also possible to add arbitrary metadata (such as titles and
descriptions) to the content items, by providing these in a separate CSV
file.

Installation
------------

First, add ``transmogrify.filesystem`` as a dependency of your product in
your ``setup.py``, and include its configuration in ``configure.zcml``::

    <include package="transmogrify.filesystem" />

Usage
-----

You can use ``transmogrify.filesystem`` in a pipeline like this::

    [transmogrifier]
    pipeline =
        data
        constructor
        schema
        savepoint

    [data]
    blueprint = transmogrify.filesystem
    directory = my.package:data/root
    ignored =
        re:.*\.svn.*

    [constructor]
    blueprint = collective.transmogrifier.sections.constructor

    [schema]
    blueprint = plone.app.transmogrifier.atschemaupdater

    [savepoint]
    blueprint = collective.transmogrifier.sections.savepoint
    every = 50

This will scan the directory ``data`` inside the Python package ``my.package``
for files and directories, but will ignore any ``.svn`` directories and their
contents. The source will yield items suitable for passing to the standard
Transmogrifier content constructor and the schema updated from
`plone.app.transmogrifier <http://pypi.python.org/pypi/plone.app.transmogrifier>`_.

Adding metadata
***************

Transmogrifier will re-create the directory structure and files in
Plone, but there is no information here to set titles or descriptions for
created items.

You can, however, add additional metadata to files by using a CSV file. For
example, say you had a CSV file like this::

    path,title,description
    /foo,Foo,A file
    /foo/bar,Bar,Another file

The headers in this file indicate the field names for additional data. One of
the columns must have a heading of ``path``, and should contain file paths
relative to the Transmogrifier context (normally the Plone site root), with
a leading slash, as shown here. These paths will be matched against the files
loaded from the data directory.

Subsequent columns are passed along as-is, so in this case, the ``title`` and
``description`` fields will be set as given in the CSV file.

To use this file, use the ``metadata`` key, e.g.::

    [data]
    blueprint = transmogrify.filesystem
    directory = my.package:data/root
    metadata = my.package:data/metadata.csv
    ignored =
        re:.*\.svn.*

Available options
-----------------

The available options are:

``directory`` (required)
    The directory from which files are read. Subdirectories should reflect
    the eventual path of images and files uploaded. May be given as an
    absolute path, a path relative to the current working directory, or a
    package reference (e.g. ``my.package:foo/bar``).
``metadata``
    A CSV file containing metadata. See above. May be given as an absolute
    path, a path relative to the current working directory, or a package
    reference (e.g. ``my.package:foo/bar``).
``require-metadata``
    If set to True, only files with matching metadata are included.
    Directories are always included regardless. Defaults to False.
``delimiter``
    A character that delimits data in your Metadata CSV file.
``strict``
    If this is set to True, transmogrify.filesystem will break if it finds
    a row of data in Metadata CSV which field-count does not match
    field-count of the first row in the CSV file.
``folder-type``
    The portal type for folders to create (if required). Defaults to
    'Folder'.
``file-type``
    The portal type for files. Defaults to 'File'.
``file-field``
    The name of the field to use for file (non-image) content. Defaults
    to ``file``, which is the name for a standard ATFile.
``image-type``
    The portal type for images. Defaults to 'Image'.
``image-field``
    The name of the field to use for image content. Defaults to ``image``,
    which is the name for a standard ATImage.
``wrap-data``
    By default, file data will be wrapped into an OFS.File or OFS.Image
    object. Set this option to False to get the raw data, as a string.
``default-mime-type``
    The default file type for content where the mimetype cannot be
    guessed. Defaults to ``application/octet-stream``.
``ignored``
    A list of paths and/or regular expressions (prefixed with ``re:`` or
    ``regexp:`` to skip).

Output
------

The yielded dictionaries will have the following keys:

``_type``
    Portal type name. Will be one of ``folder-type`` (Folder),
    ``file-type`` (File) or ``image-type`` (Image).

``_path``
    The ZODB path for the new item. This is based on the folder structure
    from which files were read.

For images and files, two additional keys are included:

``_mimetype``
    The mimetype, as guessed from the file extension. The default, if no
    adequate guess can be made, is ``application/octet-stream``.

Image field name (as set with ``file-field`` or ``image-field``)
    The contents of the file.

In addition, any keys from matching rows in the metadata CSV file, if
specified, will be included. The values will all be strings.
