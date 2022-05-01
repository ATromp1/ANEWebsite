import os

def static_file_hash_processor(request):
    ## Adds the static_hash variable to context dict on every view.
    ## It is current commit hash as a query on the end of the filename.
    ## This is to avoid caching errors when pushing CSS changes.
    return {'static_hash': os.environ.get('static_hash') or ""}
