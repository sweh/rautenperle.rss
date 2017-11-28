from bs4 import BeautifulSoup
import urllib.request

XML = """
<?xml version="1.0" encoding="UTF-8" ?>
  <rss version="2.0">

  <channel>
    <title>rautenperle.com</title>
    <link>https://www.rautenperle.com</link>
    <description>Mein Schatz</description>
    {items}
  </channel>
</rss>"""

XML_ITEM = """
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description>{description}</description>
    </item>"""


def generate():
    fp = urllib.request.urlopen("http://www.rautenperle.com")
    mybytes = fp.read()
    html = mybytes.decode("utf8")
    fp.close()
    soup = BeautifulSoup(html, 'html.parser')
    storyelem = soup.find('h1').find('a')
    items = XML_ITEM.format(title=storyelem.find('span').contents[0].strip(),
                            link='http://www.rautenperle.com' + storyelem.attrs['href'],
                            description='')
    for item in soup.find_all('h2'):
        try:
            linkelem = item.find('a')
            title = linkelem.contents[0].strip()
            url = 'http://www.rautenperle.com' + linkelem.attrs['href']
            preview = ''
            while not preview:
                item = item.nextSibling
                if item.__class__.__name__ == 'Tag':
                    preview = item.find('p').contents[0].strip()
            items += XML_ITEM.format(title=title, link=url, description=preview)
        except Exception:
            continue
    print(XML.format(items=items))


generate()
