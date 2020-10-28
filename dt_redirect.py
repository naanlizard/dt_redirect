from http.server import HTTPServer, BaseHTTPRequestHandler
import os

import praw


class Redirect(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header('Location', find_dt(self.path))
        self.end_headers()

    def log_message(self, *_):
        print(
            f'{self.headers["X-Real-IP"]}:{self.command}:{self.path}'
            f':{self.headers["User-Agent"]}'
        )


def find_dt(path = ''):
    url = 'https://www.reddit.com/r/neoliberal'
    for submission in neoliberal.search('Discussion Thread', sort='new'):
        if submission.author == 'jobautomator':
            url = submission.url
            break
    if path.strip('/') == 'dt/old':
        url = url.replace('www', 'old')
    return(url)


if __name__ == "__main__":
    reddit = praw.Reddit(
        client_id = os.environ['client_id'],
        client_secret = os.environ['client_secret'],
        refresh_token = os.environ['refresh_token'],
        user_agent = 'linux:dt_redirect:v1.1 (by /u/jenbanim)'
    )
    neoliberal = reddit.subreddit('neoliberal')
    HTTPServer(("", 8080), Redirect).serve_forever()
