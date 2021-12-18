# oj.sjtucs.com maintaining scripts
Scripts for generating pages hosted over oj.sjtucs.com.

## Contributing Code

### Submitting solutions

1. Prepare your solutions with a (GitHub, recommended) repository.
2. Fork this repository, and create your configuration file under `./answer-sources`. Read the format chapter below carefully.
3. Check your code with `./solution_check.py` in the root folder
4. Make a pull request to this repository.

### Bugs, misleading contents, &c.

Please open an issue under this repository.

## configuration file format

**Notice**: The OJ has renewed it's question numbering. The old OJ's question is now merged into the new one, where its numbers
has increased by 10000. 

The configuration file is located under `./answer-sources`, with extension `.yaml`.

```yaml
author: your_display_name
```
set your name being displayed on the website. If space is needed you should add quotes like "Your display name".
```yaml
link: https://example.com
```
(optional) Will not be used.
```yaml
git-repo: git@github.com:someone/reponame.git
```
Enter your git repo in, and only in ssh format like above. HTTPS is not allowed.
```yaml
type: direct
```
**direct** your cpp file, and path, can be located with numbers only.
**recursive** your cpp file can be determined by numbers, but they are located in irrecognizable folders. Then we'll traverse your whole folder to find the cpp file.
```yaml
private: true
```
(optional, default set to false)
**false** your repository is set to public.
**true** your repository is set to private. You need to at least grant `victrid` your repository's access to have them displayed on the website.
```yaml
old: false
```
(optional, default set to false)
**false** your OJ looks like [this](https://acm.sjtu.edu.cn/OnlineJudge/), which is put in use around 2021. 
**true** your OJ looks like [this](https://acm.sjtu.edu.cn/OnlineJudge-old/), which is put in use before around 2021. The OJ has renewed it's question numbering. The old OJ's question is now merged into the new one, where its numbers has increased by 10000. 
```yaml
route: "path/to/[NUMBER].cpp"
```
if type is set to direct, route should the the direct path to your solutions.
if type is set to recursive, route should be the corresponding file name, without path.