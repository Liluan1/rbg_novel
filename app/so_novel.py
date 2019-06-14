from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from config import Config, BLACK_DOMAIN, RULES, LATEST_RULES, USER_AGENT


def fetch(client, url, novels_name):
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


def data_extraction_for_web_so(client, html):
    try:
        try:
            title = html.find('h3').find('a').get_text()
            url = html.find('h3').find('a').get('href', None)
        except Exception as e:
            print(e)
            url, title = None, None
            return None

        netloc = urlparse(url).netloc
        if not url or 'baidu' in url or 'baike.so.com' in url or netloc in BLACK_DOMAIN:
            return None
        is_parse = 1 if netloc in RULES.keys() else 0
        is_recommend = 1 if netloc in LATEST_RULES.keys() else 0
        time = ''
        timestamp = 0
        return {'title': title, 'url': url.replace('index.html', '').replace('Index.html', ''), 'time': time,
                'is_parse': is_parse,
                'is_recommend': is_recommend,
                'timestamp': timestamp,
                'netloc': netloc}
    except Exception as e:
        print(e)
        return None


def so_search(novels_name):
    url = Config.SO_URL
    html = fetch(client=requests, url=url, novels_name=novels_name)
    if html:
        soup = BeautifulSoup(html, 'html5lib')
        result = soup.find_all(class_='res-list')
        extra_tasks = [data_extraction_for_web_so(client=requests, html=i) for i in result]
        tasks = [i for i in extra_tasks if i is not None]
        return tasks
    else:
        return []
