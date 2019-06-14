from flask import render_template, redirect, url_for, request
import time
from ..so_novel import so_search
from ..novel_parsing import cache_novels_chapter, cache_novels_content
from . import main
from urllib.parse import urlparse
from config import RULES
from operator import itemgetter


@main.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route("/search", methods=['GET'])
def search():
    start = time.time()
    name = str(request.args.get('wd')).strip()
    novels_keyword = name.split(' ')[0]
    if not name:
        return redirect(url_for('/'))

    # 通过搜索引擎获取检索结果
    novels_name = "{name} 小说 阅读 最新章节".format(name=name)
    parse_result = so_search(novels_name=novels_name)
    # https://www.cnblogs.com/gongxr/p/7291714.htm
    result_sorted = sorted(parse_result,reverse=True,key=itemgetter('is_parse', 'timestamp'))
    return render_template('result.html', name=novels_keyword, time='%.2f' % (time.time() - start), result=result_sorted,
                           count=len(parse_result))


@main.route("/chapter")
def chapter():
    """
    返回小说章节目录页
    : content_url   这决定当前U页面url的生成方式
    : url           章节目录页源url
    : novels_name   小说名称
    :return         小说章节内容页
    """
    url = request.args.get('url')
    novels_name = request.args.get('novels_name')
    netloc = urlparse(url).netloc
    if netloc not in RULES.keys():
        return redirect(url)
    content_url = RULES[netloc].content_url
    content = cache_novels_chapter(url=url, netloc=netloc)
    if content:
        content = str(content).strip('[],, Jjs').replace(', ', '').replace('onerror', '').replace('js', '').replace(
            '加入书架', '')
        return render_template(
            'chapter.html', novels_name=novels_name, url=url, content_url=content_url, soup=content)
    else:
        return ('解析失败，请重新刷新一次，或者访问源网页：{url}'.format(url=url))


@main.route("/content")
def content():
    """
    返回小说章节内容页
    : content_url   这决定当前U页面url的生成方式
    : url           章节内容页源url
    : chapter_url   小说目录源url
    : novels_name   小说名称
    :return         小说章节内容页
    """
    url = request.args.get('url', None)
    chapter_url = request.args.get('chapter_url', None)
    novels_name = request.args.get('novels_name', None)
    name = request.args.get('name', '')
    # 当小说内容url不在解析规则内 跳转到原本url
    netloc = urlparse(url).netloc
    if netloc not in RULES.keys():
        return redirect(url)
    # 拼接小说目录url
    book_url = "/chapter?url={chapter_url}&novels_name={novels_name}".format(
        chapter_url=chapter_url,novels_name=novels_name)
    if url == chapter_url:
        return redirect(book_url)
    content_url = RULES[netloc].content_url
    content_data = cache_novels_content(url=url, netloc=netloc)
    if content_data:
        try:
            content = content_data.get('content', '获取失败')
            next_chapter = content_data.get('next_chapter', [])
            title = content_data.get('title', '').replace(novels_name, '')
            name = title if title else name
            # 破坏广告链接
            content = str(content).strip('[]Jjs,').replace('http', 'hs').replace('.js', '').replace('();', '')
            return render_template('content.html', name=name, url=url, bookmark=0, book=0, content_url=content_url,
                                   chapter_url=chapter_url, novels_name=novels_name, next_chapter=next_chapter, soup=content)
        except Exception as e:
            print(e)
            return redirect(book_url)
    else:
       return ('parse_error:{url}'.format(url=url))


