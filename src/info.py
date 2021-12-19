# General information
TITLE = "Minizinc Data Service API"
VERSION = "1.0.0"
DESCRIPTION = """
The Minzinc Data Service API provides endpoints for uploading, download, and managing user files.
"""

# Info about upload.
UPLOAD = {
    'name': 'Upload',
    'description': "Endpoints for uploading a file for a user."
}


# Info about listing.
FILES = {
    'name': 'Minizinc',
    'description': "Endpoints for listing and deleting users and their files"
}





TAGS_METADATA = [UPLOAD, FILES]