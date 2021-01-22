from bs4 import BeautifulSoup
from flask import Flask, render_template, request
import requests
import urllib.parse

app = Flask(__name__)
app.secret_key = 'vnkdjnfjknflwgr2#'


class WikiPage:
    def __init__(self, url):
        self.url = requests.get(url, timeout=(3, 30)).url
        print("Created object " + self.url)
        self._links = []
        self._links_by_count = {}
        self._links_as_dict = {}
        self._sorted_links_and_titles = []

    def links(self):
        if not self._links:
            response = requests.get(self.url, timeout=(3, 30))
            content = BeautifulSoup(response.content, 'html.parser')
            tags = content.find_all(lambda tag: tag.name == 'a' and tag.get('href') is not None)
            urls = [tag.get('href') for tag in tags]
            for url in [tag.get('href') for tag in tags]:
                if self.is_valid(url):
                    self._links.append("https://en.wikipedia.org" + url)
        print(self._links)
        return self._links

    def links_by_count(self):
        if self._links_by_count is None:
            link_dict = dict()
            for link in self.links():
                if link not in link_dict:
                    link_dict[link] = 1
                else:
                    link_dict[link] += 1
            return link_dict

    def is_valid(self, url=None):
        if not url:
            url = self.url
        conditions = (lambda url: not url.startswith('#'),
                      lambda url: not url.endswith('.jpg'),
                      lambda url: url.startswith('/wiki/'),
                      lambda url: all(char not in url for char in [':', '#']),
                      lambda url: not url.endswith('Main_Page'),
                      lambda url: '_(identifier)' not in url)
        return all([condition(url) for condition in conditions])

    def as_text(self, url=None):
        if not url:
            url = self.url
        return urllib.parse.unquote(url).split('/')[-1].replace('_', ' ')

    def links_as_dict(self):
        if not self._links_as_dict:
            self._links_as_dict = {self.as_text(link): link for link in self.links()}
        print(self._links_as_dict)
        return self._links_as_dict

    def sorted_links_and_titles(self):
        if not self._sorted_links_and_titles:
            self._sorted_links_and_titles = list(sorted(self.links_as_dict().items(), key=lambda link: link[0]))
        return self._sorted_links_and_titles


@app.route('/', methods=['GET', 'POST'])
def game():
    main_page_url = 'https://en.wikipedia.org/wiki/Main_Page'

    origin = None
    current = None
    dest = None
    jumps = 0

    if request.method == 'POST':
        form = request.form
        print("User submitted form:")
        print('\n'.join([str(key) + ": " + str(value) for key, value in form.items()]))

        origin = WikiPage(form['origin'])
        dest = WikiPage(form['dest'])

        if main_page_url in request.form.values():
            current = origin
        else:
            next_ = WikiPage(form['next'])
            print("Moving to page " + next_.url)
            current = next_
            jumps = int(form['jumps']) + 1

        links = current.sorted_links_and_titles()
    else:
        main_page = WikiPage(main_page_url)
        origin = main_page
        current = main_page
        dest = main_page
        links = []

    return render_template('degrees.html',
                           origin_url=origin.url,
                           current_url=current.url,
                           dest_url=dest.url,
                           origin_title=origin.as_text(),
                           current_title=current.as_text(),
                           dest_title=dest.as_text(),
                           links=links,
                           jumps=jumps)


if __name__ == '__main__':
    app.run()
