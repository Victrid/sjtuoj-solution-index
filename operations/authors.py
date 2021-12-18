import hashlib
import os
import re
import subprocess
from os.path import isfile, join
from typing import Optional

import yaml

from operations.helpers import log


def get_authors():
    author_info = []
    for root, dirs, files in os.walk("./answer-sources", topdown=False):
        for name in files:
            with open(os.path.join(root, name), 'r') as stream:
                try:
                    author_dict = yaml.safe_load(stream)
                    md5 = hashlib.md5()
                    md5.update(author_dict["author"].encode("UTF-8"))
                    author_dict["authorhash"] = md5.hexdigest()
                    author_info.append(author_dict)
                except yaml.YAMLError:
                    log.error("SJTUOJ Update Service: Load error in file" +
                              os.path.join(root, name)
                              )
                except:
                    log.error(
                            "SJTUOJ Update Service: Unknown error happened in function get_authors()."
                            )
                    exit(-1)
    return author_info


def git_pull(author_info):
    if os.path.exists("./.gitrepo"):
        if not os.path.isdir("./.gitrepo"):
            log.error("SJTUOJ Update Service: .gitrepo exists and is not a dir. aborting.")
            exit(-1)
    else:
        os.makedirs("./.gitrepo")
        gitignore = open("./.gitrepo/.gitignore", "w+")
        gitignore.write("*\n")
        gitignore.close()
    for author in author_info:
        if "authorhash" not in author:
            log.error("SJTUOJ Update Service: Author name and hash should not be ignored.")
            continue
        if (os.path.exists(os.path.join("./.gitrepo", author["authorhash"]))):
            subprocess.run(["git", "-C", os.path.join("./.gitrepo",
                                                      author["authorhash"]
                                                      ), "pull", "origin"], capture_output=True
                           )
        else:
            subprocess.run(["git", "clone", author["git-repo"], os.path.join(
                    "./.gitrepo", author["authorhash"]
                    )], capture_output=True
                           )
        log.debug("SJTUOJ Update Service: author: {} updated.".format(author["author"]))


def guess_lang(extension):
    extension_map = {
        "cpp": "cpp",
        "cxx": "cpp",
        "c":   "c",
        "py":  "java"
        }
    if extension in extension_map:
        return extension_map[extension]
    else:
        return ""


def wrap_source_file(author_info, filename):
    _, extension = os.path.splitext(filename)
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(filename, 'r', encoding="gb18030") as f:
            content = f.read()
    git_star = ""
    if "private" in author_info and author_info["private"] is True:
        pass
    else:
        loc = re.search(r"git@github.com:(.*)\.git", author_info["git-repo"])
        if loc is not None:
            git_star = '<a class="github-button" href="https://github.com/{}" data-icon="octicon-star" data-show-count="true" aria-label="Star!"></a>'.format(
                    loc.group(1)
                    )

    wrapped = "\n## {}'s solution {}\n\n```{}\n{}\n```\n".format(author_info["author"], git_star, guess_lang(extension),
                                                                 content
                                                                 )
    return wrapped


def get_author_solution(author_info: dict, number: int) -> tuple[bool, Optional[str]]:
    # old solution compatible
    if "old" in author_info and author_info["old"] is True:
        if number < 10000:
            return False, None
        else:
            number = number - 10000

    if "type" not in author_info:
        log.error("SJTUOJ Update Service: type must be indicated.")
        return False, None

    author_base = join("./.gitrepo", author_info["authorhash"])

    if author_info["type"] == "direct":
        filename = join(author_base, author_info["route"].replace("[NUMBER]", str(number)))
        if isfile(filename):
            return True, wrap_source_file(author_info, filename)
    elif author_info["type"] == "recursive":
        file_name = join(author_base, author_info["route"].replace("[NUMBER]", str(number)))  # default
        if isfile(file_name):
            return True, wrap_source_file(author_info, file_name)
        for root, dirs, files in os.walk(author_base, topdown=False):
            for name in files:
                if name == (author_info["route"].replace("[NUMBER]", str(number))):
                    file_name = join(root, name)
                    return True, wrap_source_file(author_info, file_name)
        return False, None
    else:
        log.error("SJTUOJ Update Service: type must be indicated.")
        return False, None
    return False, None
