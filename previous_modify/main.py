# from tool import *
#
# def main():
#     # 设置 requests cookie 值，可以通过浏览器或其他方式获取
#     login_flag = input('是否登录？输入Y确定\n')
#     if login_flag == 'Y':
#         login_flag = True
#         cookie_user = input('请输入你的cookie：\n')
#         cookie = {'Cookie': cookie_user}
#         get_cookies()
#     else:
#         login_flag = False
#         cookie = ''
#     # LOFTER用户名
#     LOF_ID = input('请输入你的LOFTER用户名：\n')
#
#     # 构造 GET 请求，并设置 cookies 参数
#     response = requests.get('https://{}.lofter.com/'.format(LOF_ID), cookies=cookie)
#
#     # 处理响应结果
#     if response.status_code == 200:
#         user_response = 'N'
#         print('登录请求成功')
#         # 处理响应内容
#     else:
#         print('登录请求失败，请检查cookie是否正确\n')
#         user_response = input('是否要结束程序？输入Y退出\n')
#         cookie = ''
#
#     if user_response != 'Y':
#
#         # 获取文章链接列表
#         article_links = get_article_links(cookie, LOF_ID)
#
#         # 把全部链接写入txt
#         save_txt_name = 'article_links.txt'
#         write_list_to_file(article_links, save_txt_name)
#         print('{}篇博文链接已经成功写入article_links.txt'.format(len(article_links)))
#
#         # 遍历文章链接获取具体文章内容
#         html_choice = input('是否要生成html文件？输入N退出\n')
#         md_choice = input('是否要生成markdown文件？输入N退出\n')
#
#         filenum = 0
#         for url in article_links:
#             # 如果没有生成操作则直接结束
#             if html_choice == 'N' and md_choice == 'N':
#                 break
#
#             filenum += 1
#             # 获取html内容
#             print('{}. 正在执行{}'.format(filenum, url))
#             html = get_html(url, login_flag, cookie)
#
#             # 编写文件序号
#             if filenum <= 999:
#                 file_num = '{:03d}'.format(filenum)
#             else:
#                 file_num = str(filenum)
#
#             #保存为html文件
#             if html_choice != 'N':
#                 get_article_html(html, LOF_ID, file_num)
#
#             # 保存为md文件
#             if md_choice != 'N':
#                 get_article_md(html, LOF_ID, file_num)
#
#
#
#         print('成功获取{}篇文章，程序结束'.format(filenum))
#
#
#
#
#
#     else:
#         print('程序结束')
#
#
#
#
# if __name__ == '__main__':
#     print("abc")
#     main()
#
#
#
from tool import *
import os
import requests
import time


def main():
    # 登录处理
    login_flag = input('是否登录？输入Y确定\n')
    if login_flag == 'Y':
        login_flag = True
        cookie_user = input('请输入你的cookie：\n')
        cookie = {'Cookie': cookie_user}
        get_cookies()
    else:
        login_flag = False
        cookie = ''

    # LOFTER用户名
    LOF_ID = input('请输入你的LOFTER用户名：\n')

    # 检查登录请求
    response = requests.get('https://{}.lofter.com/'.format(LOF_ID), cookies=cookie)
    if response.status_code == 200:
        print('登录请求成功')
    else:
        print('登录请求失败，请检查cookie是否正确\n')
        user_response = input('是否要结束程序？输入Y退出\n')
        if user_response == 'Y':
            return
        cookie = ''

    # 文章链接处理：如果已保存则加载，否则获取
    article_links_file = 'article_links.txt'
    if os.path.exists(article_links_file):
        with open(article_links_file, 'r', encoding='utf-8') as f:
            article_links = [line.strip() for line in f if line.strip()]
        print('从文件中加载了 {} 篇博文链接'.format(len(article_links)))
    else:
        article_links = get_article_links(cookie, LOF_ID)
        write_list_to_file(article_links, article_links_file)
        print('{}篇博文链接已经成功写入article_links.txt'.format(len(article_links)))

    # 读取上次的处理进度（已处理文章数），从进度文件中恢复
    progress_file = 'progress.txt'
    start_index = 0
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                start_index = int(f.read().strip())
            print('从进度文件中恢复，已处理 {} 篇文章'.format(start_index))
        except Exception as e:
            print("读取进度文件出错，重新从头开始处理。", e)
            start_index = 0

    # 允许用户指定起始序号覆盖进度文件的值
    custom_start = input("请输入自定义起始序号（直接回车使用上次进度 {}）：".format(start_index))
    if custom_start.strip() != "":
        try:
            start_index = int(custom_start.strip())
            print("自定义起始序号设为 {}".format(start_index))
        except Exception as e:
            print("输入无效，将使用上次进度：{}".format(start_index))

    html_choice = input('是否要生成html文件？输入N退出\n')
    md_choice = input('是否要生成markdown文件？输入N退出\n')

    total_articles = len(article_links)
    for i in range(start_index, total_articles):
        url = article_links[i]
        print('{}. 正在执行{}'.format(i + 1, url))
        try:
            html = get_html(url, login_flag, cookie)
            # 设置文件编号格式
            if i + 1 <= 999:
                file_num = '{:03d}'.format(i + 1)
            else:
                file_num = str(i + 1)
            # 保存HTML文件
            if html_choice != 'N':
                get_article_html(html, LOF_ID, file_num)
            # 保存Markdown文件
            if md_choice != 'N':
                get_article_md(html, LOF_ID, file_num)

            # 处理成功后更新进度文件
            with open(progress_file, 'w') as pf:
                pf.write(str(i + 1))

        except Exception as e:
            print("处理第 {} 篇文章时出错: {}".format(i + 1, e))
            print("程序中断，已保存进度，请修复问题后重新运行程序")
            break

    print("文章处理完成或程序中断。")


if __name__ == '__main__':
    main()

