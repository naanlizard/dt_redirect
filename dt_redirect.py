from http.server import HTTPServer, BaseHTTPRequestHandler
import os

import praw

class Redirect(BaseHTTPRequestHandler):
    def __init__(self, *args):
        self.reddit = praw.Reddit(
            client_id = os.environ['client_id'],
            client_secret = os.environ['client_secret'],
            refresh_token = os.environ['refresh_token'],
            user_agent = 'linux:dt_redirect:v1.0 (by /u/jenbanim)'
        )
        self.neoliberal = self.reddit.subreddit('neoliberal')
        super().__init__(*args)

    def _find_dt(self):
        url = 'https://www.reddit.com/r/neoliberal'
        for submission in self.neoliberal.search('Discussion Thread', sort='new'):
            if submission.author == 'jobautomator':
                url = submission.url
                break
        if self.path == '/dt/old':
            url = url.replace('www', 'old')
        return(url)

    def do_GET(self):
        self.send_response(302)
        self.send_header('Location', self._find_dt())
        self.end_headers()

HTTPServer(("", 8080), Redirect).serve_forever()
