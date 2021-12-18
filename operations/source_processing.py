import json
import math
import os
import re
import urllib
from urllib import parse, request

import markdown
import requests
from bs4 import BeautifulSoup

from operations.helpers import less_request, log

login_id = os.getenv('ACMOJ_SECRET', "6b4d4ec1-f3bc-4694-88d2-1f1a5646464e")

cookies = {'Login_ID': login_id}
headers = {"Cookie": "Login_ID={}".format(login_id)}


def question_cache(question_id: int) -> dict:
    question_number = str(question_id)

    if os.path.exists("./.question_cache"):
        if not os.path.isdir("./.question_cache"):
            log.error("SJTUOJ Update Service: .question_cache exists and is not a dir. aborting.")
            exit(-1)
    else:
        os.makedirs("./.question_cache")

    if os.path.exists('./.question_cache/{}.json'.format(question_id)):
        with open('./.question_cache/{}.json'.format(question_id), 'r') as f:
            return json.load(f)
    else:
        less_request()
        # Now getting them from API
        data = {'problem_id': question_number}
        response = requests.post('https://acm.sjtu.edu.cn/OnlineJudge/api/get_detail', cookies=cookies, data=data)
        content = json.loads(response.content)
        with open('./.question_cache/{}.json'.format(question_number), 'w+') as f:
            json.dump(content, f)
        log.debug("SJTUOJ Update Service: retrieved {}.".format(question_number))
        return content


def get_max_pages() -> int:
    html_doc = 'https://acm.sjtu.edu.cn/OnlineJudge/problems'
    req = urllib.request.Request(html_doc, headers=headers)
    less_request()
    webpage = urllib.request.urlopen(req)
    html = webpage.read()
    soup = BeautifulSoup(html, features="lxml")
    max_pg = soup.find("a", string=" >> ").attrs["href"]
    return int(urllib.parse.parse_qs(urllib.parse.urlparse(max_pg).query, encoding='utf-8')["page"][0])


# get the available index
def available_index():
    if not os.path.exists('./.question_cache/.complete'):
        available = set()
        for page in range(1, get_max_pages() + 1):
            log.debug("SJTUOJ Update Service: checking index page {}".format(page))
            html_doc = 'https://acm.sjtu.edu.cn/OnlineJudge/problems?page=' + \
                       str(page)
            req = urllib.request.Request(html_doc, headers=headers)
            less_request()
            webpage = urllib.request.urlopen(req)
            html = webpage.read()
            soup = BeautifulSoup(html, features="lxml")
            table = soup.find(id="problem_list")
            question_list = table.find_all('tr', recursive=False)
            for item in question_list:
                avail = int(item.find("th").contents[0])
                available.add(avail)
            log.debug("SJTUOJ Update Service: current index length {}".format(len(available)))
        log.debug("SJTUOJ Update Service: index checking complete.")
        with open('./.question_cache/.complete', 'w'):
            pass
        return available
    else:
        question_list = os.listdir("./.question_cache")
        available = set()
        for file in question_list:
            match = re.match(r"^([0-9]+)\.json$", file)
            if match:
                available.add(int(match.group(1)))

        start_page = math.ceil(len(set(filter(lambda x: x < 10000, available))) / 20)
        current_length = 0
        while current_length != len(available):
            current_length = len(available)
            log.debug("SJTUOJ Update Service: checking index page {}".format(start_page))
            html_doc = 'https://acm.sjtu.edu.cn/OnlineJudge/problems?page=' + \
                       str(start_page)
            req = urllib.request.Request(html_doc, headers=headers)
            less_request()
            webpage = urllib.request.urlopen(req)
            html = webpage.read()
            soup = BeautifulSoup(html, features="lxml")
            table = soup.find(id="problem_list")
            question_list = table.find_all('tr', recursive=False)
            for item in question_list:
                avail = int(item.find("th").contents[0])
                available.add(avail)
            start_page += 1
            log.debug("SJTUOJ Update Service: current index length {}".format(len(available)))
        log.debug("SJTUOJ Update Service: index checking complete.")
        return available


# API result to data being printed
def wrap_question(question_description: dict) -> str:
    description = ""
    md = markdown.Markdown()
    if question_description["Description"] != "None":
        description += "<h3>题目描述</h3>\n\n{}\n\n".format(md.convert(question_description["Description"]))
    if question_description["Input"] != "None":
        description += "<h3>输入格式</h3>\n\n{}\n\n".format(md.convert(question_description["Input"]))
    if question_description["Output"] != "None":
        description += "<h3>输出格式</h3>\n\n{}\n\n".format(md.convert(question_description["Output"]))
    if question_description["Example_Input"] != "None":
        description += "<h3>样例输入</h3>\n\n{}\n\n".format(md.convert(question_description["Example_Input"]))
    if question_description["Example_Output"] != "None":
        description += "<h3>样例输出</h3>\n\n{}\n\n".format(md.convert(question_description["Example_Output"]))
    if question_description["Data_Range"] != "None":
        description += "<h3>数据范围</h3>\n\n{}\n\n".format(md.convert(question_description["Data_Range"]))
    return description
