import yaml


class FileMetadata(yaml.YAMLObject):
    """
    The class of file metadata.

    Attributes:
            title (str): A title for the file
            filename (str): The name of the file
            filepath (str): The full path of the file in the filesystem.
            md5 (str): An MD5 hash of the file
            dateCreated (str): The date of when the file was created.
            dateModified (str): The date of when the file was last modified.
            originUrl (str): The web location of the original file.
            etag (str): The eTag for the web location of the file.
            originOrg (str): The agent responsible for providing the source file.
            script (str): The name of the program that created the file.
            status (str): A status flag in processing this entity
    """

    yaml_tag = "!FileMetadata"
    title = None
    filename = None
    filepath = None
    md5 = None
    dateCreated = None
    dateModified = None
    originUrl = None
    etag = None
    originOrg = None
    script = None
    status = None

    def __init__(
        self,
        title=None,
        filename=None,
        filepath=None,
        md5=None,
        dateCreated=None,
        dateModified=None,
        originUrl=None,
        etag=None,
        originOrg=None,
        script=None,
        status=None,
    ):
        if title is not None:
            self.title = title
        if filename is not None:
            self.filename = filename
        if filepath is not None:
            self.filepath = filepath
        if md5 is not None:
            self.md5 = md5
        if dateCreated is not None:
            self.dateCreated = dateCreated
        if dateModified is not None:
            self.dateModified = dateModified
        if originUrl is not None:
            self.originUrl = originUrl
        if etag is not None:
            self.etag = etag
        if originOrg is not None:
            self.originOrg = originOrg
        if script is not None:
            self.script = script
        if status is not None:
            self.status = status
