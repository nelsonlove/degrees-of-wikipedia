from bs4 import BeautifulSoup
from flask import Flask, render_template, request
import requests
import urllib.parse

app = Flask(__name__)
app.secret_key = 'vnkdjnfjknflwgr2#'


class Page:
    def __init__(self, url, follow_redirect=None):
        self.url = url
        if follow_redirect:
            self.url = self.get_redirect_url()

    def get_redirect_url(self):
        return requests.get(self.url, timeout=(3, 30)).url

    def text(self):
        return urllib.parse.unquote(self.url).split('/')[-1].replace('_', ' ')

    def get_links(self):
        response = requests.get(self.url, timeout=(3, 30))
        content = BeautifulSoup(response.content, 'html.parser')
        selector = lambda tag: tag.name == 'a' and tag.get('href') is not None
        links = [tag.get('href') for tag in content.find_all(selector)]
        validator = lambda x: all([cond(x) for cond in (
            lambda x: x.startswith('/wiki/'),
            lambda x: all(char not in x for char in [':', '#']),
            lambda x: not x.endswith('Main_Page'),
            lambda x: not x.endswith('.jpg'),
            lambda x: '_(identifier)' not in x)])
        valid_and_expanded_links = ['https://en.wikipedia.org' + link for link in filter(validator, links)]
        sorted_and_unique_links = sorted(set(valid_and_expanded_links), key=lambda x: x)
        return [Page(link) for link in sorted_and_unique_links]

    def __eq(self, other):
        return self.url == other.url


@app.route('/', methods=['GET', 'POST'])
def play():
    print(request)
    if not request.method == 'POST':
        return render_template('degrees.html')
    print(request.form)
    if 'current' in request.form:
        origin = Page(request.form['origin'])
        dest = Page(request.form['dest'])
        jumps = int(request.form['jumps']) + 1
        current = Page(request.form['next'])
    else:
        origin = Page(request.form['origin'], follow_redirect=True)
        dest = Page(request.form['dest'], follow_redirect=True)
        jumps = 0
        current = origin
    links = current.get_links() if current.url != dest.url else []
    return render_template('degrees.html', origin=origin, dest=dest, current=current, jumps=jumps, links=links)


if __name__ == '__main__':
    app.run()
