#!/bin/python
import yaml
import sys
import os
import hashlib
import subprocess
import time
import glob
import shutil
import re
import chardet
import codecs
import urllib
import request
import time
from bs4 import BeautifulSoup

update_script_version = "2.0.0"


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
                    sys.stderr.write("Load error in file\n" +
                                     os.path.join(root, name)+"\n")
                except:
                    sys.stderr.write(
                        "Unknown error happend in function get_authors().\n")
                    exit(-1)
    return author_info


def git_pull(author_info):
    if os.path.exists("./.gitrepo"):
        if not os.path.isdir("./.gitrepo"):
            sys.stderr.write(".gitrepo exists and is not a dir. aborting.\n")
            exit(-1)
    else:
        os.makedirs("./.gitrepo")
        gitignore = open("./.gitrepo/.gitignore", "w+")
        gitignore.write("./*\n")
        gitignore.close()
    for author in author_info:
        if "authorhash" not in author:
            sys.stderr.write("Author name and hash should not be ignored.")
            continue
        if(os.path.exists(os.path.join("./.gitrepo", author["authorhash"]))):
            subprocess.run(["git", "-C", os.path.join("./.gitrepo",
                                                      author["authorhash"]), "fetch", "origin"], capture_output=True)
        else:
            subprocess.run(["git", "clone", author["git-repo"], os.path.join(
                "./.gitrepo", author["authorhash"])], capture_output=True)


class Counter(object):
    def __init__(self, start=0):
        self.num = start

    def count(self):
        self.num += 1
        return self.num


def question_cache(i, counter):
    question_number = str(i)
    question_number = question_number.zfill(4)
    if os.path.exists("./.question_cache"):
        if not os.path.isdir("./.question_cache"):
            sys.stderr.write(
                ".question_cache exists and is not a dir. aborting.\n")
            exit(-1)
    else:
        os.makedirs("./.question_cache")
        gitignore = open("./.question_cache/.gitignore", "w+")
        gitignore.write("./*\n")
        gitignore.close()
    if os.path.exists('./.question_cache/'+question_number+'.title.md'):
        pass
    else:
        z = counter.count()
        if z % 5 == 0:
            time.sleep(2)
        if z % 25 == 0:
            time.sleep(10)
        if z % 125 == 0:
            time.sleep(120)
        html = request.urlopen(request.Request(
            'https://acm.sjtu.edu.cn/OnlineJudge/problem/'+question_number)).read()
        soup = BeautifulSoup(html, features="lxml")
        taglist = soup.find_all('div', attrs={'class': 'page-header'})
        for tag in taglist:
            title = open('./.question_cache/' +
                         question_number+'.title.md', 'w+')
            title.write(tag.h1.get_text()[6:])
            title.close()
        question = open('./.question_cache/' +
                        question_number+'.question.md', 'w+')
        question.write(soup.article.prettify())
        question.close()
    title = open('./.question_cache/'+question_number+'.title.md', 'r')
    question = open('./.question_cache/'+question_number+'.question.md', 'r')
    return title, question


def available_index(counter):
    i = 1
    lld = []
    while 1 == 1:
        html_doc = 'https://acm.sjtu.edu.cn/OnlineJudge/problems?page=' + \
            str(i)
        req = request.Request(html_doc)
        webpage = request.urlopen(req)
        z = counter.count()
        if z % 5 == 0:
            time.sleep(2)
        if z % 25 == 0:
            time.sleep(10)
        if z % 125 == 0:
            time.sleep(120)
        html = webpage.read()
        soup = BeautifulSoup(html, features="lxml")
        tbd = soup.find_all('tbody')
        tabl = tbd[0].find_all('tr')
        if len(tabl):
            for tg in tabl:
                ll = tg.find('td').get_text()
                lld = lld+re.findall('\d+', ll)
            i += 1
        else:
            break
    llb = []
    for item in lld:
        llb.append(int(item))
    return llb


def indexgen(avail):
    i = 1000
    ind = open('./.tmp/index.md', 'w+')
    while i < len(avail):
        number = str(i)
        number = number.zfill(4)
        if i == 1000:
            ind.write('\n# Index Page\n')
            ind.write(
                '\n <style type="text/css">a.deleted:link {color:#CE0000}\n a.deleted:visited {color:#CE0000}\n a.deleted:hover {color:#EA0000}\n a:deleted:active {color:#FF0000}</style>\n')
        if i % 1000 == 0:
            st = str(i)
            st = st.zfill(4)
            ind.write('\n## '+st+'+\n')
        if i % 100 == 0:
            st = str(i)
            st = st.zfill(4)
            ind.write('\n### '+st+'+\n')
        if avail[i] == -1:
            line = '<a href="'+number + '/" class="deleted">'+number+'</a>'
            ind.write(line+'\n')
        if avail[i] == 1:
            line = '['+number+']('+number+'.md)'
            ind.write(line+'\n')
        if avail[i] == 0:
            line = '<font color="#CCCCCC">'+number+'</font>'
            ind.write(line+'\n')
        if i % 10 == 9:
            ind.write('\n')
        i += 1
    ind.close()


def arrange(author, number, output):
    if "type" not in author:
        sys.stderr.write("type must be indicated.")
        return 0
    author_base = os.path.join("./.gitrepo", author["authorhash"])
    if author["type"] == "direct":
        try:
            srcfile = open(os.path.join(
                author_base, author["route"].replace("[NUMBER]", str(number))), 'r')
            output.write('\n## '+author["author"] + '\'s solution')
            if "private" in author and author["private"] == True:
                pass
            else:
                loc = re.search(r"git@github.com:(.*)\.git",
                                author["git-repo"])
                if loc != None:
                    output.write(' <a class="github-button" href="https://github.com/'+loc.group(1) +
                                 '" data-icon="octicon-star" data-show-count="true" aria-label="Star!"></a>')
            output.write('\n\n```cpp\n')
            output.writelines(srcfile.readlines())
            output.write('\n```\n')
            srcfile.close()
            return 1
        except UnicodeDecodeError:
            srcfile.close()
            srcfile = open(os.path.join(
                author_base, author["route"].replace("[NUMBER]", str(number))), 'r', encoding="gb18030")
            output.writelines(srcfile.readlines())
            output.write('\n```\n')
            srcfile.close()
            return 1
        except FileNotFoundError:
            return 0
    else:
        file_name = os.path.join(
            author_base, author["route"].replace("[NUMBER]", str(number)))  # default
        for root, dirs, files in os.walk(author_base, topdown=False):
            for name in files:
                if name == (author["route"].replace("[NUMBER]", str(number))):
                    file_name = os.path.join(root, name)
        try:
            srcfile = open(file_name, 'r')
            output.write('\n## '+author["author"] + '\'s solution')
            if "private" in author and author["private"] == True:
                pass
            else:
                loc = re.search(r"git@github.com:(.*)\.git",
                                author["git-repo"])
                if loc != None:
                    output.write(' <a class="github-button" href="https://github.com/'+loc.group(1) +
                                 '" data-icon="octicon-star" data-show-count="true" aria-label="Star!"></a>')
            output.write('\n\n```cpp\n')
            output.writelines(srcfile.readlines())
            output.write('\n```\n')
            srcfile.close()
            return 1
        except UnicodeDecodeError:
            srcfile.close()
            srcfile = open(file_name, 'r', encoding="gb18030")
            output.writelines(srcfile.readlines())
            output.write('\n```\n')
            srcfile.close()
            return 1
        except FileNotFoundError:
            return 0
    return 0


def generate_all(author_info):
    if os.path.exists("./.tmp"):
        if not os.path.isdir("./.tmp"):
            sys.stderr.write(".tmp exists and is not a dir. aborting.\n")
            exit(-1)
    else:
        os.makedirs("./.tmp")
    os.system("rm -rf ./.tmp/*")
    gitignore = open("./.tmp/.gitignore", "w+")
    gitignore.write("./*\n")
    gitignore.close()
    counter = Counter()
    lindex = available_index(counter)
    avail = [0] * (max(lindex)+1)
    z = 0
    for i in lindex:
        title, question = question_cache(i, counter)
        number = str(i)
        number = number.zfill(4)
        z += 1
        output_name = './.tmp/'+number+'.md'
        title_with_num = number+' '+title.read()
        title.close()
        output = open(output_name, 'w+')
        output.write("---\ntitle: "+title_with_num +
                     '---\n\n<script async defer src="https://buttons.github.io/buttons.js"></script>\n# '+title_with_num+'\n')
        # output.write('!!! success "推荐"\n')
        # output.write(
        #     '\t[迟先生](https://skyzh.xyz)搞了一个[上海交通大学计算机系本科作业参考](https://github.com/skyzh/awesome-cs)存储库，大家点这个按钮就可以传送并立刻<a class="github-button" href="https://github.com/skyzh/awesome-cs" data-icon="octicon-star" data-show-count="true" aria-label="Star!"></a>一个\n\n')
        # output.write(
        #     '\t如果你对网站的实现感兴趣，或是对本站和脚本的实现有新的想法，请加入[telegram吹水群](https://t.me/koraboreta)。\n\n')
        output.write(
            '<details>\n<summary><a href="https://acm.sjtu.edu.cn/OnlineJudge/problem/'+str(number)+'">题目</a></summary>\n\n')
        output.write(question.read())
        question.close()
        output.write("\n</details>\n")
        solution_count = 0
        for author in author_info:
            solution_count += arrange(author, number, output)
        if solution_count != 0:
            avail[i] = 1
        else:
            output.write(
                '\n## Oops! 本题目还没有解答！\n太难了，助教老师们编题的速度，已经超过了解题的速度！\n\n但是，如果你已经AC了，如果可以的话，请您参考[添加](/add)页面，与大家一起分享你的题解！\n\n')
            avail[i] = -1
        output.close()
    indexgen(avail)


def main():
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))
    author_info = get_authors()
    git_pull(author_info)
    generate_all(author_info)
    if os.path.exists("./mkdocs/docs/nr"):
        if not os.path.isdir("./mkdocs/docs/nr"):
            sys.stderr.write("nr exists and is not a dir. aborting.\n")
            exit(-1)
    else:
        os.makedirs("./mkdocs/docs/nr")
    if(os.path.exists("./mkdocs/site")):
        pass
    else:
        proc = subprocess.run(
            ["git", "clone", "git@github.com:SJTU-OJ/SJTU-OJ.github.io.git", "./mkdocs/site"], capture_output=True)
    subprocess.run(["rm", "./mkdocs/nr/*"], capture_output=True)
    subprocess.run(["cp", "./.tmp/*", "./mkdocs/nr/"], capture_output=True)
    os.chdir("./mkdocs")
    subprocess.run(["mkdocs", "build"], capture_output=True)
    proc = subprocess.run(["git", "-C", "./site",
                           "diff-files", "--", "nr"], capture_output=True)
    if proc.stdout:
        print("Changed. Commiting...")
        print(proc.stdout.decode("UTF-8"))
        subprocess.run(["git", "-C", "./site", "add", "."],
                       capture_output=True)
        subprocess.run(["git", "-C", "./site", "commit", "-m",
                        "v"+update_script_version+" Data Update "+time.time()], capture_output=True)
        subprocess.run(["git", "-C", "./site", "push",
                        "origin", "master"], capture_output=True)
        subprocess.run(["git", "-C", "/static/sjtuoj",
                        "fetch"], capture_output=True)  # This is a call to the server to update.
    else:
        print("Nothing have changed. Quitting...")


if __name__ == '__main__':
    main()
