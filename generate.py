from bs4 import BeautifulSoup
import urllib.request
import subprocess
import json
import re

XML = """\
<?xml version="1.0" encoding="UTF-8" ?>
  <rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">

  <channel>
    <title>rautenperle.com</title>
    <link>https://www.rautenperle.com</link>
    <description>Mein Schatz</description>
    <atom:link href="https://www.wehrmann.it/rautenperle.xml" rel="self" type="application/rss+xml" />
    {items}
  </channel>
</rss>"""

XML_ITEM = """
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <pubDate>{date}</pubDate>
      <guid>{link}</guid>
      <enclosure url="{lead_image_url}" length="2048" type="image/jpeg" />
      <description><![CDATA[{description}]]></description>
      <content:encoded><![CDATA[{content}]]></content:encoded>
    </item>"""


# <pubDate>Tue, 27 Oct 2020 12:18:16 +0000</pubDate>
GUIDS = []

def get_json(url):
    return json.loads(
        subprocess.Popen(f"/usr/bin/mercury-parser {url} --add-extractor /home/sweh/rautenperle.rss/rautenperle_date.js", shell=True, stdout=subprocess.PIPE).stdout.read())

def generate():
    fp = urllib.request.urlopen("http://www.rautenperle.com")
    mybytes = fp.read()
    html = mybytes.decode("utf8")
    fp.close()
    soup = BeautifulSoup(html, 'html.parser')
    storyelem = soup.find('h1').find('a')
    url = 'http://www.rautenperle.com' + storyelem.attrs['href']
    p = get_json(url)
    GUIDS.append(url)
    items = XML_ITEM.format(
        title=storyelem.find('span').contents[0].strip().replace('&', 'und'),
        link='http://www.rautenperle.com' + storyelem.attrs['href'],
        lead_image_url=p.get('lead_image_url', 'https://www.wehrmann.it/rautenperle.jpg'),
        description=p['excerpt'],
        date=p['date_published'],
        content=p['content'])
    for item in soup.find_all('h2'):
        try:
            linkelem = item.find('a')
            title = linkelem.contents[0].strip().replace('&', 'und')
            url = 'http://www.rautenperle.com' + linkelem.attrs['href']
            if url in GUIDS:
                continue
            GUIDS.append(url)
            p = get_json(url)
            items += XML_ITEM.format(
                title=title,
                link=url,
                lead_image_url=p.get('lead_image_url', 'https://www.wehrmann.it/rautenperle.jpg'),
                description=p['excerpt'],
                date=p['date_published'],
                content=p['content'])
        except Exception:
            continue
    print(XML.format(items=items))


generate()
