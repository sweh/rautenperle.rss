from bs4 import BeautifulSoup
from mercury_parser import ParserAPI
import configparser
import hashlib
import requests
import urllib.request
import os

XML = """
<?xml version="1.0" encoding="UTF-8" ?>
  <rss version="2.0">

  <channel>
    <title>Spiegel Daily</title>
    <link>https://daily.spiegel.de</link>
    <description>Täglich ab 17 Uhr das Neueste aus der Welt</description>
    {items}
  </channel>
</rss>"""

XML_ITEM = """
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description>{description}</description>
    </item>"""


def get_id(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()


def get_mercury_url(url):
    config = configparser.ConfigParser()
    config.read('config.ini')
    plain_cookie = config['spiegel']['plain_cookie']

    cj = requests.utils.cookiejar_from_dict(dict(p.split('=') for p in plain_cookie.split('; ')))
    sess = requests.Session()
    sess.cookies = cj

    html = sess.get(url).text
    id = url.split('/')[-1]

    with open(id, 'w') as f:
        f.write(html)

    return id


def generate():
    config = configparser.ConfigParser()
    config.read('config.ini')
    MAPIKEY = config['mercury']['apikey']
    mercury = ParserAPI(api_key=MAPIKEY)
    fp = urllib.request.urlopen("http://daily.spiegel.de")
    mybytes = fp.read()
    html = mybytes.decode("utf8")
    fp.close()
    soup = BeautifulSoup(html, 'html.parser')
    items = {}
    for item in soup.find_all('a'):
        try:
            url = item.attrs['href']
            title = item.find('h2').contents[0] + ' - ' + item.find('h3').contents[0]
            murl = get_mercury_url(url)
            p = mercury.parse('https://www.wehrmann.it/' + murl)
            os.remove(murl)
            preview = p.content or item.find('main').find('div').contents[0].strip()
            items[url] = (title, preview)
        except Exception:
            continue
    sitems = ''
    for url, item in items.items():
        title, preview = item
        sitems += XML_ITEM.format(title=title, link=url, description=preview)
    # KURZMELDUNGEN
    for item in soup.find('amp-accordion').find_all('h3'):
        title = item.contents[0]
        url = 'https://daily.spiegel.de/#' + get_id(title)
        preview = ' '.join(n.contents[0] for n in item.parent.parent.parent.find_all('p'))
        sitems += XML_ITEM.format(title=title, link=url, description=preview)
    print(XML.format(items=sitems))


generate()
