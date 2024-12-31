import time
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta, timezone
import praw

# ---------------------------------------------------------------
# Setup Logging
# ---------------------------------------------------------------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.WARNING),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------
# We'll search the public subreddit /r/neoliberal for recent posts (last 36 hours).
# Then we check if they are by jobautomator, containing "Discussion Thread".
DISCUSSION_AUTHOR = os.environ.get("DISCUSSION_AUTHOR", "jobautomator")
DISCUSSION_SUBREDDIT = os.environ.get("DISCUSSION_SUBREDDIT", "neoliberal")

# We'll keep a simple cache to avoid hitting Reddit's API on every request.
CACHE = {
    "dt_url": None,             # The last known Discussion Thread URL
    "cached_at": 0.0,           # When we last fetched it (Unix timestamp)
}

# 36 hours in seconds
TIME_WINDOW_SECONDS = 36 * 3600

# We'll say once we fetch, we won't refetch for another X seconds (e.g., 15 min).
CACHE_TTL = 15 * 60  # 15 minutes


def find_recent_discussion_thread() -> str:
    """
    Search /r/neoliberal for posts from the last 36 hours,
    posted by DISCUSSION_AUTHOR, containing 'Discussion Thread' in the title.

    Returns:
        str: The URL of the most recent matching post,
             or fallback to https://www.reddit.com/r/neoliberal if none is found.
    """
    logger.info("Searching subreddit for Discussion Thread...")

    # We'll figure out the cutoff time in Unix seconds
    cutoff = time.time() - TIME_WINDOW_SECONDS

    try:
        subreddit = reddit.subreddit(DISCUSSION_SUBREDDIT)

        # We fetch up to 100 newest submissions to see if there's a match
        # (Adjust limit if needed)
        matches = []
        for submission in subreddit.new(limit=100):
            # If the post is older than 36 hours, no need to consider it
            if submission.created_utc < cutoff:
                continue

            # Check if author & title match
            if (
                submission.author
                and submission.author.name.lower() == DISCUSSION_AUTHOR.lower()
                and "discussion thread" in submission.title.lower()
            ):
                matches.append(submission)

        # Sort matched posts by creation time descending
        matches.sort(key=lambda s: s.created_utc, reverse=True)

        if matches:
            # The first item is the most recent match
            most_recent = matches[0]
            logger.info(
                f"Found a Discussion Thread by u/{DISCUSSION_AUTHOR}: "
                f"'{most_recent.title}' -> {most_recent.url} "
                f"(created_utc={most_recent.created_utc})"
            )
            return most_recent.url
        else:
            logger.warning("No matching Discussion Thread found in the last 36 hours.")
            return f"https://www.reddit.com/r/{DISCUSSION_SUBREDDIT}"
    except Exception as e:
        logger.exception(f"Failed to search the subreddit. Using fallback. Error: {e}")
        return f"https://www.reddit.com/r/{DISCUSSION_SUBREDDIT}"


def get_discussion_thread_url() -> str:
    """
    Return a cached Discussion Thread URL if fresh,
    otherwise fetch it from Reddit using find_recent_discussion_thread().
    """
    now = time.time()
    # Check if our cache is still fresh
    if CACHE["dt_url"] and (now - CACHE["cached_at"]) < CACHE_TTL:
        logger.debug("Returning cached Discussion Thread (within cache TTL).")
        return CACHE["dt_url"]

    # Otherwise, fetch a fresh one
    logger.info("Cache expired or empty. Fetching new Discussion Thread from Reddit.")
    url = find_recent_discussion_thread()
    CACHE["dt_url"] = url
    CACHE["cached_at"] = now
    return url


def rewrite_dt_url_by_path(url: str, path: str) -> str:
    """
    Same logic for dt/old, dt/stream, dt/compact transformations.
    """
    cleaned_path = path.strip('/')
    if cleaned_path == 'dt/old':
        url = url.replace('www', 'old')
    elif cleaned_path == 'dt/stream':
        url = url.replace('reddit.com', 'reddit-stream.com')
    elif cleaned_path == 'dt/compact':
        url = url.replace('www', 'i')
    return url


# ---------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------
class Redirect(BaseHTTPRequestHandler):
    def do_GET(self):
        logger.debug(f"Received GET request: Path={self.path}")
        self.send_response(302)
        try:
            discussion_url = get_discussion_thread_url()
            final_url = rewrite_dt_url_by_path(discussion_url, self.path)
            self.send_header('Location', final_url)
            logger.debug(f"Redirecting to: {final_url}")
        except Exception:
            logger.exception("Error while processing request; falling back to subreddit.")
            self.send_header('Location', f"https://www.reddit.com/r/{DISCUSSION_SUBREDDIT}")
        self.end_headers()

    def log_message(self, format, *args):
        # Overriding to reduce server console noise; rely on our logger
        return


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting Discussion Thread redirect server...")

    # Create our Reddit instance (just needs read scope)
    reddit = praw.Reddit(
        client_id=os.environ['client_id'],
        client_secret=os.environ['client_secret'],
        refresh_token=os.environ['refresh_token'],
        user_agent='DiscussionThreadRedirect/1.0 (by /u/your_bot_username)'
    )
    logger.info("Reddit instance created successfully.")

    logger.info(f"Will search /r/{DISCUSSION_SUBREDDIT} for 'Discussion Thread' by u/{DISCUSSION_AUTHOR} in the last 36 hours.")

    logger.info("Starting HTTP server on port 8080.")
    HTTPServer(("", 8080), Redirect).serve_forever()