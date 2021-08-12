"""A simple webserver for redirecting traffic to latest discussion thread"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import os

import praw


class Redirect(BaseHTTPRequestHandler):
    """Handle incoming requests"""

    def do_GET(self):
        """Handle HTTP GET requests"""
        self.send_response(302)
        try:
            self.send_header('Location', find_dt(self.path))
        except Exception:
            self.send_header('Location', 'https://reddit.com/r/neoliberal')
        self.end_headers()

    def log_message(self, *_):
        # Nginx logs are sufficient
        pass


def find_dt(path = ''):
    """Locate the current DT using praw.

    Assumes the existence of a 'neoliberal' object in outer scope
    """
    url = 'https://www.reddit.com/r/neoliberal'
    for submission in neoliberal.search('Discussion Thread', sort='new'):
        if submission.author == 'jobautomator':
            url = submission.url
            break
    if path.strip('/') == 'dt/old':
        url = url.replace('www', 'old')
    elif path.strip('/') == 'dt/stream':
        url = url.replace('reddit.com', 'reddit-stream.com')
    return(url)


if __name__ == "__main__":
    """Create our Reddit instance and run the webserver indefinitely"""
    reddit = praw.Reddit(
        client_id = os.environ['client_id'],
        client_secret = os.environ['client_secret'],
        refresh_token = os.environ['refresh_token'],
        user_agent = 'linux:dt_redirect:v1.1 (by /u/jenbanim)'
    )
    neoliberal = reddit.subreddit('neoliberal')
    HTTPServer(("", 8080), Redirect).serve_forever()
