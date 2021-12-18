#!/bin/python
import os
import subprocess
import sys

from operations.authors import get_authors
from operations.file_processing import generate_all
from operations.helpers import log


def call_mkdocs():
    if os.path.exists("./mkdocs/docs/nr"):
        if not os.path.isdir("./mkdocs/docs/nr"):
            log.error("SJTUOJ Update Service: nr exists and is not a dir. aborting.")
            exit(-1)
    else:
        os.makedirs("./mkdocs/docs/nr")
    subprocess.run("rm -rf ./mkdocs/site", shell=True, capture_output=True)
    os.makedirs("./mkdocs/site")
    subprocess.run("rm ./mkdocs/docs/nr/*", shell=True, capture_output=True)
    subprocess.run("cp ./.tmp/* ./mkdocs/docs/nr/",
                   shell=True, capture_output=True
                   )
    os.chdir("./mkdocs")
    subprocess.run(["mkdocs", "build"], capture_output=True)
    log.info("SJTUOJ Update Service: MkDocs build complete.")
    # No trailing!
    location = os.getenv('PRODUCT_LOC', None)
    if location is not None:
        subprocess.run("rm -rf {}/*".format(location), shell=True, capture_output=True)
        subprocess.run("mv ./mkdocs/site {}".format(location), shell=True, capture_output=True)
    log.info("SJTUOJ Update Service: Quit.")


def main():
    log.info("SJTUOJ Update Service: started.")
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

    author_info = get_authors()

    # git_pull(author_info)

    log.info("SJTUOJ Update Service: repository pull complete.")

    generate_all(author_info)

    log.info("SJTUOJ Update Service: file generation complete.")

    call_mkdocs()


if __name__ == '__main__':
    main()
