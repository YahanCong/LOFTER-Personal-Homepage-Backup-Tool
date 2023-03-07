import requests
from bs4 import BeautifulSoup
import time
import os
import html2text
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import re
import json

def get_cookies():
    driver = webdriver.Chrome()
    driver.get('https://www.lofter.com/front/login/')
    time.sleep(20)
    with open ('cookies.txt', 'w') as f:
        f.write(json.dumps(driver.get_cookies()))
        driver.close()

def write_list_to_file(lst, filename):
    """将列表中的数据分行写入文本文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in lst:
            f.write(str(item) + '\n')


def write_file(subdir_name, file_name, content, type):
    # 获取当前脚本的路径
    script_path = os.path.dirname(os.path.abspath(__file__))

    # 子目录的名称
    subdir_name = subdir_name

    # 构造子目录的路径
    subdir_path = os.path.join(script_path, subdir_name)

    # 如果子目录不存在，创建子目录
    if not os.path.exists(subdir_path):
        os.makedirs(subdir_path)

    # 构造要写入的文件的路径
    file_path = os.path.join(subdir_path, file_name)

    # 写入文件
    if type == 'html':
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    if type == 'md':
        write_list_to_file(content, file_path)


def get_article_links(cookie, LOF_ID):

    article_links = []
    page_num = 0
    while True:
        # 博客页面的 URL
        blog_url = 'https://{}.lofter.com/?page='.format(LOF_ID)+str(page_num)
        # 发送博客页面请求
        response = requests.get(blog_url, cookies=cookie)
        soup = BeautifulSoup(response.content, 'html.parser')
        article_num = 0
        # 获取本页所有的文章链接
        for link in soup.find_all('a'):
            if link.text == '查看全文':
                article_links.append(link.get('href'))
                article_num += 1

        if article_num == 0:
            break
        page_num += 1
        print('成功获取第{}页，现在成功获取文章链接数量: {}'.format(page_num, len(article_links)))

        #调整爬虫速度
        time.sleep(0.5)
    print('总共获取{}页，成功获取文章链接数量: {}'.format(page_num, len(article_links)))


    return article_links


# 获取文章内容
def get_html(url, login_flag, cookie):
    response = requests.get(url, cookies=cookie)
    # 获取原网页源码
    html_soup = BeautifulSoup(response.content, 'html.parser')
    iframe = html_soup.find('iframe', {'id': 'comment_frame'})
    comment_url = 'http:' + iframe['src']

    # 获取评论
    # 创建浏览器驱动
    driver = webdriver.Chrome()
    if login_flag:
        driver.get(comment_url)
        driver.delete_all_cookies()
        # 添加 cookie
        with open('cookies.txt', 'r') as f:
            cookie_list = json.load(f)
            for cookie in cookie_list:
                driver.add_cookie(cookie_dict=cookie)

        # 刷新页面
        driver.refresh()

    # 打开网页
    driver.get(comment_url)

    #等待加载
    time.sleep(2.5)
    driver.execute_script("window.scrollBy(0, 15000)")

    # 获取“查看更多”按钮
    load_more = driver.find_element(By.XPATH, "//div[@class=\"bcmtmore s-bd2\"]")

    # 循环点击“查看更多”按钮直到全部展开
    while True:
        try:
            # 点击按钮
            load_more.click()
            time.sleep(0.7)

            # 模拟下拉
            actions = ActionChains(driver)
            actions.move_to_element(load_more).perform()
            time.sleep(0.7)


        except:
            # 找不到“查看更多”按钮，结束循环
            break


    # 获取iframe中的html源码
    iframe_html = driver.page_source

    # 解析html源码
    soup_iframe = BeautifulSoup(iframe_html, 'html.parser')

    # 关闭浏览器驱动
    driver.quit()

    # 获取需要的内容，这里假设是class为bcmt的div
    bcmt_div = soup_iframe.find('div', {'class': 'bcmt'})

    # 将iframe内容插入原html
    target_div = html_soup.find('iframe', {'id': 'comment_frame'})
    target_div.replace_with(bcmt_div)

    return html_soup


# 保存html格式
def get_article_html(soup, LOF_ID, filenum):

    # 获取文章标题
    title_div = soup.find('h2', {'class': 'title'})
    if title_div != None:
        title = title_div.get_text().strip().replace('\n', '')
    else:
        title = filenum

    # 获取文章发布时间
    time_div = soup.find('div', {'class': 'itm clear time'})
    if time_div != None:
        time = time_div.get_text().strip()
    else:
        time = 'Default'

    # 设置保存文件路径和文件名
    subdir_html = '{}_html'.format(LOF_ID) # html文件
    file_title = re.sub(r'[^\w\-_\. ]', '', title)
    filename_html = '{}_{}_{}_{}.html'.format(LOF_ID, filenum, file_title, time) # html文件

    # 保存文章原html格式文件
    write_file(subdir_html, filename_html, soup.prettify(), 'html')


#保存markdown格式
def get_article_md(soup, LOF_ID, filenum):
    # 获取文章标题
    title_div = soup.find('h2', {'class': 'title'})
    if title_div != None:
        title = title_div.get_text().strip().replace('\n', '')
    else:
        title = filenum

    # 获取文章发布时间
    time_div = soup.find('div', {'class': 'itm clear time'})
    if time_div != None:
        time = time_div.get_text().strip()
    else:
        time = 'Default'

    # 设置保存文件路径和文件名
    subdir_md = '{}_markdown'.format(LOF_ID)  # md文件
    file_title = re.sub(r'[^\w\-_\. ]', '', title)
    filename_md = '{}_{}_{}_{}.md'.format(LOF_ID, filenum, file_title, time)  # md文件

    # 获取文章tag
    tag_list = soup.find('div', {'class': 'itm clear tag'})
    if tag_list != None:
        tag_list = [a.text.replace('#', '') for a in tag_list.find_all('a')]
        tags = ','.join(tag_list)
    else:
        tags = None

    # 获取文章作者
    author = soup.find('a', {'class': 'blogtitle'}) .get_text().strip()


    # 获取文章类别
    if soup.find('div', {'class': 'post article'}) != None:
        categories = 'Text'
    elif soup.find('div', {'class': 'post photo'}) != None:
        categories = 'Photo'
    elif soup.find('div', {'class': 'post video'}) != None:
        categories = 'Video'
    else:
        categories = None

    md_content = []
    # 生成markdown内容
    # 文章基本信息 div_info
    info = '---\ntitle: \"{}\"\ndate: {}\ntags: [{}]\nauthor: \"{}\"\ncategories: [{}]\n---'.format(title, time, tags, author, categories)
    md_content.append(info)
    md_content.append('\n\n\n')

    # 文章内容 div_content
    #标题
    if title_div != None:
        for i in title_div:
            title_md = html2text.html2text(str(i))
            md_content.append("##"+title_md)

    # 图片
    img_list = [a.get('bigimgsrc') for a in soup.find_all('a', {'class': 'imgclasstag'})]
    img = [f'<img src="{img}">' for img in img_list]

    if img_list != None:
        for i in img:
            md_content.append(i)
        md_content.append('\n\n')

    # 文字
    html_text = soup.find_all('div', {'class': 'text'})
    for i in html_text:
        md_text = html2text.html2text(str(i)).strip()
        md_content.append(md_text)
        md_content.append('\n')

    # 热度和评论数量
    hot = ' '.join([div.text.strip() for div in soup.find_all('div', {'class': 'nctitle'})])
    md_content.append('\n\n\n\n\n\n\n')
    md_content.append(hot)

    # 获取评论链接以及内容
    comment_soup = soup
    for tag in comment_soup.find_all('div', class_='bcmtlstj'):
        s_fcs = tag.find_all('span', class_='s-fc3 itag', style='display:none;')
        for s_fc in s_fcs:
            s_fc.extract()
    comment_html = comment_soup.find_all('div', class_='bcmtlstj')
    md_content.append('\n\n\n\n\n---------------------------------------\n')
    for i in comment_html:
        comment_md = html2text.html2text(str(i)).strip()
        md_content.append(comment_md)
        md_content.append('\n\n')


    # 保存文章原html格式文件
    write_file(subdir_md, filename_md, md_content, 'md')



