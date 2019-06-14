from config import USER_AGENT, RULES
from bs4 import BeautifulSoup
import re
from collections import OrderedDict
from urllib.parse import urljoin
import requests
import chardet


def get_html_by_requests(url, headers, timeout=15):

    try:
        response = requests.get(url=url, headers=headers, timeout=timeout)
        response.raise_for_status()
        content = response.content
        charset = chardet.detect(content)
        text = content.decode(charset['encoding'])
        return text
    except Exception as e:
        print(e)
        return None


def novels_list(text):
    rm_list = ['后一个', '天上掉下个']
    for i in rm_list:
        if i in text:
            return False
        else:
            continue
    return True


def extract_pre_next_chapter(chapter_url, html):
    """
    获取单章节上一页下一页
    :param chapter_url:
    :param html:
    :return:
    """
    next_chapter = OrderedDict()
    try:
        # 参考https://greasyfork.org/zh-CN/scripts/292-my-novel-reader
        next_reg = r'(<a\s+.*?>.*[第上前下后][一]?[0-9]{0,6}?[页张个篇章节步].*?</a>)'
        judge_reg = r'[第上前下后][一]?[0-9]{0,6}?[页张个篇章节步]'
        # 这里同样需要利用bs再次解析
        next_res = re.findall(next_reg, html.replace('<<', '').replace('>>', ''), re.I)
        str_next_res = '\n'.join(next_res)
        next_res_soup = BeautifulSoup(str_next_res, 'html5lib')
        for link in next_res_soup.find_all('a'):
            text = link.text or ''
            text = text.replace(' ', '')
            if novels_list(text):
                is_next = re.search(judge_reg, text)
                # is_ok = is_chapter(text)
                if is_next:
                    url = urljoin(chapter_url, link.get('href')) or ''
                    next_chapter[text[:5]] = url

        return next_chapter
    except Exception as e:
        return next_chapter


def cache_novels_content(url, netloc):
    headers = {
        'user-agent': USER_AGENT
    }

    html = get_html_by_requests(url=url, headers=headers)
    if html:
        soup = BeautifulSoup(html, 'html5lib')
        selector = RULES[netloc].content_selector
        if selector.get('id', None):
            content = soup.find_all(id=selector['id'])
        elif selector.get('class', None):
            content = soup.find_all(class_=selector['class'])
        else:
            content = soup.find_all(selector.get('tag'))
        if content:
            # 提取出真正的章节标题
            title_reg = r'(第?\s*[一二两三四五六七八九十○零百千万亿0-9１２３４５６７８９０]{1,6}\s*[章回卷节折篇幕集]\s*.*?)[_,-]'
            title = soup.title.string
            extract_title = re.findall(title_reg, title, re.I)
            if extract_title:
                title = extract_title[0]
            else:
                title = soup.find('h1').get_text()
            if not title:
                title = soup.title.string
            next_chapter = extract_pre_next_chapter(chapter_url=url, html=str(soup))
            content = [str(i) for i in content]
            data = {
                'content': str(''.join(content)),
                'next_chapter': next_chapter,
                'title': title
            }
        else:
            data = None
        return data
    return None


def cache_novels_chapter(url, netloc):
    headers = {
        'user-agent': USER_AGENT
    }

    html = get_html_by_requests(url=url, headers=headers)
    if html:
        soup = BeautifulSoup(html, 'html5lib')
        selector = RULES[netloc].chapter_selector
        if selector.get('id', None):
            content = soup.find_all(id=selector['id'])
        elif selector.get('class', None):
            content = soup.find_all(class_=selector['class'])
        else:
            content = soup.find_all(selector.get('tag'))
        # 清除所有图片链接 https://www.cnblogs.com/yizhenfeng168/p/6999355.html
        img_plants = soup.find_all('img')
        for img in img_plants:
            img.extract()
        # 防止章节被display:none
        return str(content).replace('style', '') if content else None
    return None