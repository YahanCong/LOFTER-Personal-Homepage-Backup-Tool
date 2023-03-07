from tool import *

def main():
    # 设置 requests cookie 值，可以通过浏览器或其他方式获取
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

    # 构造 GET 请求，并设置 cookies 参数
    response = requests.get('https://{}.lofter.com/'.format(LOF_ID), cookies=cookie)

    # 处理响应结果
    if response.status_code == 200:
        user_response = 'N'
        print('登录请求成功')
        # 处理响应内容
    else:
        print('登录请求失败，请检查cookie是否正确\n')
        user_response = input('是否要结束程序？输入Y退出\n')
        cookie = ''

    if user_response != 'Y':

        # 获取文章链接列表
        article_links = get_article_links(cookie, LOF_ID)

        # 把全部链接写入txt
        save_txt_name = 'article_links.txt'
        write_list_to_file(article_links, save_txt_name)
        print('{}篇博文链接已经成功写入article_links.txt'.format(len(article_links)))

        # 遍历文章链接获取具体文章内容
        html_choice = input('是否要生成html文件？输入N退出\n')
        md_choice = input('是否要生成markdown文件？输入N退出\n')

        filenum = 0
        for url in article_links:
            # 如果没有生成操作则直接结束
            if html_choice == 'N' and md_choice == 'N':
                break

            filenum += 1
            # 获取html内容
            print('{}. 正在执行{}'.format(filenum, url))
            html = get_html(url, login_flag, cookie)

            # 编写文件序号
            if filenum <= 999:
                file_num = '{:03d}'.format(filenum)
            else:
                file_num = str(filenum)

            #保存为html文件
            if html_choice != 'N':
                get_article_html(html, LOF_ID, file_num)

            # 保存为md文件
            if md_choice != 'N':
                get_article_md(html, LOF_ID, file_num)



        print('成功获取{}篇文章，程序结束'.format(filenum))





    else:
        print('程序结束')




if __name__ == '__main__':
    main()










