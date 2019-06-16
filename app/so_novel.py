from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from config import Config, BLACK_DOMAIN, RULES, LATEST_RULES, USER_AGENT


def fetch(client, url, novels_name):
    """
    获取网页源代码
    :param client:
    :param url:
    :param novels_name:
    :return:
    """
    try:
        headers = {
            'User-Agent': USER_AGENT,
            'Referer': "http://www.so.com/haosou.html?src=home"
        }
        params = {'ie': 'utf-8', 'src': 'home_suggst_personal', 'q': novels_name, }
        with client.get(url, params=params, headers=headers) as response:
            assert response.status_code == 200
            text = response.text
            return text
    except Exception as e:
        print(e)
        return None


def data_extraction_for_web_so(html):
    """
    对一条搜索结果进行解析
    :param html: 网页源代码
    :return: 一条搜索结果的解析结果
    """

    try:
        try:
            title = html.find('h3').find('a').get_text() # 标题
            url = html.find('h3').find('a').get('href', None) # url
        except Exception as e:
            print(e)
            url, title = None, None
            return None

        netloc = urlparse(url).netloc
        # 过滤黑名单
        if not url or 'baidu' in url or 'baike.so.com' in url or netloc in BLACK_DOMAIN:
            return None
        # 判断解析
        is_parse = 1 if netloc in RULES.keys() else 0
        # 判断推荐
        is_recommend = 1 if netloc in LATEST_RULES.keys() else 0
        return {'title': title, 'url': url.replace('index.html', '').replace('Index.html', ''),
                'is_parse': is_parse,
                'is_recommend': is_recommend,
                'netloc': netloc}
    except Exception as e:
        print(e)
        return None


def so_search(novels_name):
    """
    使用360搜索小说
    :param novels_name: 小说名
    :return: 搜索结果
    """
    url = Config.SO_URL
    html = fetch(client=requests, url=url, novels_name=novels_name)
    if html:
        soup = BeautifulSoup(html, 'html5lib')
        result = soup.find_all(class_='res-list')
        extra_tasks = [data_extraction_for_web_so(html=i) for i in result]
        tasks = [i for i in extra_tasks if i is not None]
        return tasks
    else:
        return []
