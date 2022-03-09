# 爬取电影《长津湖之水门桥》的影评
import requests
from lxml import etree
from tqdm import tqdm
import time
import random
import pandas as pd
import re

name_list, content_list, date_list, score_list, city_list = [], [], [], [], []
movie_name = ""

def get_city(url, i):
    time.sleep(round(random.uniform(2, 3), 2))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}
        #改为自己的cookie
    cookies = {'cookie': 'bid=E1kbkcXAFvM; __utmc=30149280; __utmz=30149280.1646712848.1.1.utmcsr=link.zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; ll="118403"; __gads=ID=462de63ae4b6273b-2203c784e2d00071:T=1646713661:RT=1646713661:S=ALNI_MZsmNha4u2qIrxpuQv0i0BXFaZ2QA; ap_v=0,6.0; __utma=30149280.474109672.1646712848.1646719256.1646787765.3; __utmt=1; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1646787867%2C%22https%3A%2F%2Fmovie.douban.com%2Fsubject%2F35613853%2Fcomments%3Fstart%3D220%26limit%3D20%26status%3DP%26sort%3Dnew_score%22%5D; _pk_ses.100001.8cb4=*; dbcl2="157713824:48zMZi+93n0"; ck=-SoD; push_noty_num=0; push_doumail_num=0; __utmv=30149280.15771; _pk_id.100001.8cb4=507bd5fd9fc85854.1646713642.2.1646787906.1646713655.; __utmb=30149280.8.10.1646787765'}  # 2018.7.25修改，
    res = requests.get(url, cookies=cookies, headers=headers)
    if (res.status_code == 200):
        print("\n成功获取第{}个用户城市信息！".format(i))
    else:
        print("\n第{}个用户城市信息获取失败".format(i))
    pattern = re.compile('<div class="user-info">.*?<a href=".*?">(.*?)</a>', re.S)
    item = re.findall(pattern, res.text)  # list类型
    return (item[0])  # 只有一个元素，所以直接返回

def get_content(id, page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        #改为自己的cookie
    cookies = {'cookie': 'bid=E1kbkcXAFvM; __utmc=30149280; __utmz=30149280.1646712848.1.1.utmcsr=link.zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; ll="118403"; __gads=ID=462de63ae4b6273b-2203c784e2d00071:T=1646713661:RT=1646713661:S=ALNI_MZsmNha4u2qIrxpuQv0i0BXFaZ2QA; ap_v=0,6.0; __utma=30149280.474109672.1646712848.1646719256.1646787765.3; __utmt=1; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1646787867%2C%22https%3A%2F%2Fmovie.douban.com%2Fsubject%2F35613853%2Fcomments%3Fstart%3D220%26limit%3D20%26status%3DP%26sort%3Dnew_score%22%5D; _pk_ses.100001.8cb4=*; dbcl2="157713824:48zMZi+93n0"; ck=-SoD; push_noty_num=0; push_doumail_num=0; __utmv=30149280.15771; _pk_id.100001.8cb4=507bd5fd9fc85854.1646713642.2.1646787906.1646713655.; __utmb=30149280.8.10.1646787765'}
    url = "https://movie.douban.com/subject/" + str(id) + "/comments?start=" + str(page * 10) + "&limit=20&sort=new_score&status=P"
    res = requests.get(url, headers=headers, cookies=cookies)
    pattern = re.compile('<div id="wrapper">.*?<div id="content">.*?<h1>(.*?) 短评</h1>', re.S)
    global movie_name
    print(movie_name)
    movie_name = re.findall(pattern, res.text)[0]  # list类型
    res.encoding = "utf-8"
    if (res.status_code == 200):
        print("\n第{}页短评爬取成功！".format(page + 1))
        print(url)
    else:
        print("\n第{}页爬取失败！".format(page + 1))

    with open('html.html', 'w', encoding='utf-8') as f:
        f.write(res.text)
        f.close()
    x = etree.HTML(res.text)
    for i in range(1, 21):   # 每页20个评论用户
        name = x.xpath('//*[@id="comments"]/div[{}]/div[2]/h3/span[2]/a/text()'.format(i))
        # 下面是个大bug，如果有人没有评分，但是评论了，那么score解析出来是日期，而日期所在位置spen[3]为空
        score = x.xpath('//*[@id="comments"]/div[{}]/div[2]/h3/span[2]/span[2]/@title'.format(i))
        date = x.xpath('//*[@id="comments"]/div[{}]/div[2]/h3/span[2]/span[3]/@title'.format(i))
        m = '\d{4}-\d{2}-\d{2}'
        try:
            match = re.compile(m).match(score[0])
        except IndexError:
            break
        if match is not None:
            date = score
            score = ["null"]
        else:
            pass
        content = x.xpath('//*[@id="comments"]/div[{}]/div[2]/p/span/text()'.format(i))
        id = x.xpath('//*[@id="comments"]/div[{}]/div[2]/h3/span[2]/a/@href'.format(i))
        try:
            city = get_city(id[0], i)  # 调用评论用户的ID城市信息获取
        except IndexError:
            city = " "
        name_list.append(str(name[0]))
        score_list.append(str(score[0]).strip('[]\''))  # bug 有些人评论了文字，但是没有给出评分
        date_list.append(str(date[0]).strip('[\'').split(' ')[0])
        content_list.append(str(content[0]).strip())
        city_list.append(city)

def main(ID, pages):
    global movie_name
    for i in tqdm(range(0, pages)):  # 豆瓣只开放500条评论
        get_content(ID, i)  # 第一个参数是豆瓣电影对应的id序号，第二个参数是想爬取的评论页数
        time.sleep(round(random.uniform(3, 5), 2))
    infos = {'name': name_list, 'city': city_list, 'content': content_list, 'score': score_list, 'date': date_list}
    data = pd.DataFrame(infos, columns=['name', 'city', 'content', 'score', 'date'])
    data.to_csv(movie_name + ".csv")  # 存储名为  电影名.csv

if __name__ == '__main__':
    main(35613853, 20)  # 评论电影的ID号+要爬取的评论页面数