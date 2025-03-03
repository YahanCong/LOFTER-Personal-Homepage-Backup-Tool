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
#     main()
#
#
#
#
#
#
#
#
#
#

from tool import *
import os
import requests
import time
import json


def main():
    ##############################
    # 1. 前置工作和登录检查
    ##############################
    # 登录及前置检查部分
    login_flag = input('是否登录？输入Y确定：\n').strip().upper() == 'Y'
    if login_flag:
        cookie_user = input('请输入你的cookie：\n').strip()
        cookie = {'Cookie': cookie_user}
        # 获取最新 cookie（这里可以将 cookies.txt 保存到特定账号文件夹中）
        get_cookies()  # 若 get_cookies() 支持传入保存路径，可修改为 get_cookies(cookies_file)
    else:
        cookie = ''

    LOF_ID = input('请输入你的LOFTER用户名：\n').strip()

    # 为每个账号创建独立的文件夹
    account_dir = os.path.join("data", LOF_ID)
    if not os.path.exists(account_dir):
        os.makedirs(account_dir)
        print(f"创建账号文件夹：{account_dir}")
    else:
        print(f"使用已有账号文件夹：{account_dir}")

    # 定义文件路径
    article_links_file = os.path.join(account_dir, "article_links.txt")
    processed_ids_file = os.path.join(account_dir, "processed_ids.txt")
    cookies_file = os.path.join(account_dir, "cookies.txt")

    # 验证登录状态
    response = requests.get(f'https://{LOF_ID}.lofter.com/', cookies=cookie)
    if response.status_code == 200:
        print('登录请求成功')
    else:
        print('登录请求失败，请检查cookie是否正确')
        if input('是否要结束程序？输入Y退出：\n').strip().upper() == 'Y':
            return
        cookie = ''
    # login_flag = input('是否登录？输入Y确定：\n').strip().upper() == 'Y'
    # if login_flag:
    #     cookie_user = input('请输入你的cookie：\n').strip()
    #     # 构造 requests 使用的 cookie 字典
    #     cookie = {'Cookie': cookie_user}
    #     # 通过 Selenium 获取最新的 cookie 并保存到 cookies.txt
    #     get_cookies()
    # else:
    #     cookie = ''
    #
    # LOF_ID = input('请输入你的LOFTER用户名：\n').strip()
    #
    # # 验证登录状态
    # response = requests.get(f'https://{LOF_ID}.lofter.com/', cookies=cookie)
    # if response.status_code == 200:
    #     print('登录请求成功')
    # else:
    #     print('登录请求失败，请检查cookie是否正确')
    #     if input('是否要结束程序？输入Y退出：\n').strip().upper() == 'Y':
    #         return
    #     cookie = ''

    ##############################
    # 2. 链接抓取与更新选择
    ##############################
    #article_links_file = 'article_links.txt'
    update_choice = input("是否更新抓取链接？输入Y更新（会抓取最新链接），输入N使用已有链接文件：\n").strip().upper()
    if update_choice == 'Y':
        # 获取最新的所有链接（例如可能抓取到1200个链接）
        all_article_links = get_article_links(cookie, LOF_ID)
        print(f"新抓取到 {len(all_article_links)} 个链接")
        # 读取已有链接（如果有的话）
        existing_links = set()
        if os.path.exists(article_links_file):
            with open(article_links_file, 'r', encoding='utf-8') as f:
                for line in f:
                    link = line.strip()
                    if link:
                        existing_links.add(link)
        # 筛选出新增链接
        new_links = [link for link in all_article_links if link not in existing_links]
        print(f"已有 {len(existing_links)} 个链接，新增 {len(new_links)} 个链接")
        # 将新增链接追加到链接文件中（保持完整历史）
        if new_links:
            with open(article_links_file, 'a', encoding='utf-8') as f:
                for link in new_links:
                    f.write(link + "\n")
        else:
            print("没有检测到新增链接。")
        # 让用户选择是只处理新增链接还是全部链接
        process_choice = input("请选择处理方式：输入1只处理新增链接；输入2处理全部链接：\n").strip()
        if process_choice == '1' and new_links:
            links_to_process = new_links
        else:
            with open(article_links_file, 'r', encoding='utf-8') as f:
                links_to_process = [line.strip() for line in f if line.strip()]
    else:
        # 不更新，直接使用已有链接文件
        if os.path.exists(article_links_file):
            with open(article_links_file, 'r', encoding='utf-8') as f:
                links_to_process = [line.strip() for line in f if line.strip()]
        else:
            # 如果链接文件不存在，则重新抓取
            links_to_process = get_article_links(cookie, LOF_ID)
            write_list_to_file(links_to_process, article_links_file)

    print(f"共需处理 {len(links_to_process)} 个链接")

    ##############################
    # 3. 文章处理与断点续传（基于 post id）
    ##############################
    html_choice = input('是否要生成 html 文件？输入 N 退出：\n').strip().upper()
    md_choice = input('是否要生成 markdown 文件？输入 N 退出：\n').strip().upper()

    # 使用 processed_ids.txt 记录已处理文章的 post id
    processed_ids_file = "processed_ids.txt"
    processed_ids = set()
    if os.path.exists(processed_ids_file):
        with open(processed_ids_file, "r", encoding="utf-8") as pf:
            for line in pf:
                pid = line.strip()
                if pid:
                    processed_ids.add(pid)
        print(f"从进度文件恢复，已处理 {len(processed_ids)} 篇文章")

    total_articles = len(links_to_process)
    for idx, url in enumerate(links_to_process, start=1):
        # 提取文章唯一标识
        post_id = extract_post_id(url)
        # 如果该文章已经处理，则跳过
        if post_id in processed_ids:
            print(f"跳过已处理文章: {post_id}")
            continue

        print(f"{idx}. 正在处理 {url}")
        try:
            html = get_html(url, login_flag, cookie)
            if html_choice != 'N':
                get_article_html(html, LOF_ID, url)  # 传入文章 URL，内部用 extract_post_id() 生成文件名
            if md_choice != 'N':
                get_article_md(html, LOF_ID, url)
            # 添加到已处理列表，并更新文件
            processed_ids.add(post_id)
            with open(processed_ids_file, "w", encoding="utf-8") as pf:
                for pid in processed_ids:
                    pf.write(pid + "\n")
        except Exception as e:
            print(f"处理文章 {idx} 时出错: {e}")
            print("程序中断，已保存进度，请修复问题后重新运行程序")
            break

    print("文章处理完成或程序中断。")


if __name__ == '__main__':
    main()

