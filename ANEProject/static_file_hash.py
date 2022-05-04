from pathlib import Path


def static_file_hash_processor(request):
    BASE_DIR = Path(__file__).resolve().parent.parent
    ## Adds the static_hash variable to context dict on every view.
    ## It is current commit hash as a query on the end of the filename.
    ## This is to avoid caching errors when pushing CSS changes.
    with open(str(BASE_DIR) + '/git_commands/git_hash', 'r') as gh:
        static_hash = gh.readlines()[0]
    gh.close()
    return {'static_hash': static_hash or ""}
