transmogrify.filesystem
=======================

Transmogrifier source for reading files from the filesystem

This package provides a `collective.transmogrifier
<http://pypi.python.org/pypi/collective.transmogrifier>`_ source for reading
data from the filesystem. It is capable of reading directories as well as
files and images.

To use it, add it as a dependency of your product in ``setup.py`` and include
its configuration in ``configure.zcml``, e.g. with::

    <include package="transmogrify.filesystem" /.

You can then use a pipeline like this::

    [transmogrifier]
    pipeline =
        data
        constructor
        schema
        savepoint

    [data]
    blueprint = transmogrify.filesystem
    directory = my.package:data
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
for files and directories. It will then yield items suitable for passing to
the standard Transmogrifier content constructor and the schema updated from
plone.app.transmogrifier.

**Note:** Transmogrifier will re-create the directory structure and files in
Plone, but there is no information here to set titles or descriptions for
created items. To do that, you will need another section in the pipeline which
can add e.g. ``title`` and ``description`` fields to the dictionary.

The available options are:

directory (required)
    The directory from which files are read. Subdirectories should reflect
    the eventual path of images and files uploaded.
folder-type
    The portal type for folders to create (if required). Defaults to
    'Folder'.
file-type
    The portal type for files. Defaults to 'File'.
file-field
    The name of the field to use for file (non-image) content. Defaults
    to ``file``, which is the name for a standard ATFile.
image-type
    The portal type for images. Defaults to 'Image'.
image-field
    The name of the field to use for image content. Defaults to ``image``,
    which is the name for a standard ATImage.
wrap-data
    By default, file data will be wrapped into an OFS.File or OFS.Image
    object. Set this option to False to get the raw data, as a string.
default-mime-type
    The default file type for content where the mimetype cannot be
    guessed. Defaults to ``application/octet-stream``.
ignored
    A list of paths and/or regular expressions (prefixed with ``re:`` or
    ``regexp:`` to skip).

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
