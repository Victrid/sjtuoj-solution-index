from operations.authors import get_author_solution
from operations.helpers import create_temp_folder
from operations.source_processing import available_index, question_cache, wrap_question


def gen_index(index, avail):
    old_questions = set(filter(lambda x: x > 10000, index))
    new_questions = set(filter(lambda x: x < 10000, index))
    index_string = """# 索引页面

<style type="text/css">
    a.deleted:link {color:#CE0000}
    a.deleted:visited {color:#CE0000}
    a.deleted:hover {color:#EA0000}
    a:deleted:active {color:#FF0000}
</style>
    
**请善用右边的目录**

"""

    index_string += "\n<center> <h2>新OJ的题目 ({} - {})</h2> </center>\n\n".format(min(new_questions), max(new_questions))

    i = 1000
    while i <= max(new_questions):
        if i % 1000 == 0:
            index_string += "\n## {}+\n\n".format(i)
        if i % 100 == 0:
            index_string += "\n### {}+\n\n".format(i)

        if i not in index or i not in avail:
            index_string += '<font color="#CCCCCC">{}</font>\n'.format(i)
        elif avail[i] is False:
            index_string += '<a href="{}/" class="deleted">{}</a>\n'.format(i, i)
        elif avail[i] is True:
            index_string += '<a href="{}/">{}</a>\n'.format(i, i)

        if i % 10 == 9:
            index_string += "\n"

        i += 1

    index_string += "\n\n<center> <h2>旧OJ的题目 ({} - {})</h2> </center>\n\n".format(min(old_questions),
                                                                                  max(old_questions)
                                                                                  )

    i = 11000

    while i <= max(old_questions):
        if i % 1000 == 0:
            has_item = False
            for number in range(i, i + 1000):
                if number in index:
                    has_item = True
                    break

            if not has_item:
                i += 1000
                continue
            index_string += "\n## {}+\n\n".format(i)

        if i % 100 == 0:
            has_item = False
            for number in range(i, i + 100):
                if number in index:
                    has_item = True
                    break

            if not has_item:
                i += 100
                continue
            index_string += "\n### {}+\n\n".format(i)

        if i % 10 == 0:
            has_item = False
            for number in range(i, i + 10):
                if number in index:
                    has_item = True
                    break

            if not has_item:
                i += 10
                continue

        if i not in index and i not in avail:
            index_string += '<font color="#CCCCCC">{}</font>\n'.format(i)
        elif avail[i] is False:
            index_string += '<a href="{}/" class="deleted">{}</a>\n'.format(i, i)
        elif avail[i] is True:
            index_string += '<a href="{}/">{}</a>\n'.format(i, i)

        if i % 10 == 9:
            index_string += "\n"
        i += 1

    with open('./.tmp/index.md', 'w+') as f:
        f.write(index_string)
    return


def generate_all(author_info_list):
    create_temp_folder()
    index = available_index()
    answer_available = {}
    for i in index:
        question_description = question_cache(i)
        number = str(i)
        output_name = './.tmp/{}.md'.format(number)
        title_with_num = "{}: {}".format(number, question_description["Title"])
        content = ""
        available = False
        for author_info in author_info_list:
            exist, solution = get_author_solution(author_info, i)
            if exist:
                content += solution
                available = True

        if not available:
            content = """
## Oops! 本题目还没有解答！
            
助教老师们编题的速度，已经超过了解题的速度！

OJ翻了一新，但本解答集还大多用的是2017-2019级，甚至更早的同学们贡献的答案。

如果你已经AC了，可以的话，请您参考[添加](/add)页面，与大家一起分享你的题解！

"""

        out_string = """---
title: {}
---

<script async defer src="https://buttons.github.io/buttons.js"></script>

# {}

<details>
<summary><a href="https://acm.sjtu.edu.cn/OnlineJudge/problem?problem_id={}">题目</a></summary>
{}
</details>

{}

        """.format(title_with_num,
                   title_with_num,
                   number,
                   wrap_question(question_description),
                   content
                   )
        with open(output_name, "w+") as f:
            f.write(out_string)
        answer_available[i] = available
    gen_index(index, answer_available)
