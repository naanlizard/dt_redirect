#!/usr/bin/env python3

from flask import Flask, redirect
import praw
import os
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

# Configure PRAW
reddit = praw.Reddit(
    client_id = os.environ['client_id'],
    client_secret = os.environ['client_secret'],
    refresh_token = os.environ['refresh_token'],
    user_agent = 'linux:dt_redirect:v1.2 (by /u/jenbanim)'
)

reddit.read_only = True

# Cache structure: store the latest discussion link and when it was posted
cached_discussion = {
    "url": None,         # e.g., "/r/something/comments/..."
    "created_utc": None  # timestamp of creation in UTC
}

def find_latest_discussion():
    """
    Return the most recent submission from u/jobautomator whose title
    contains 'Discussion Thread'. Returns a PRAW Submission object or None.
    """
    # Grab up to 10 newest submissions to be safe
    for submission in reddit.redditor("jobautomator").submissions.new(limit=10):
        if "Discussion Thread" in submission.title:
            return submission
    return None

def is_cache_expired():

    if cached_discussion["created_utc"] is None:
        return True

    creation_time = datetime.fromtimestamp(cached_discussion["created_utc"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    return (now - creation_time) >= timedelta(hours=24)

def get_discussion_link():
    """
    If the cache is empty or the cached thread is 24+ hours old, query
    Reddit for a new Discussion Thread. If found, update the cache.
    Otherwise, keep returning the old link (if it exists).
    """
    if cached_discussion["url"] is None or is_cache_expired():
        new_discussion = find_latest_discussion()
        if new_discussion:
            # Found a new thread (or at least a valid Discussion Thread),
            # so update the cache with the new link
            cached_discussion["url"] = new_discussion.permalink
            cached_discussion["created_utc"] = new_discussion.created_utc
        # If nothing new was found, either keep returning the old one
        # or remain None if no old link exists
    return cached_discussion["url"]

@app.route("/")
@app.route("/<path:subpath>")
def index(subpath=None):
    link = get_discussion_link()
    if not link:
        # If we have no valid link, fallback to the subreddit homepage
        return redirect("https://www.reddit.com/r/neoliberal", code=302)

    return_url = "https://www.reddit.com" + link
    cleaned_path = (subpath or "").strip("/")
    if cleaned_path == "dt/old":
        return_url = return_url.replace("www", "old")
    elif cleaned_path == "dt/stream":
        return_url = return_url.replace("reddit.com", "reddit-stream.com")

    return redirect(return_url, code=302)

if __name__ == "__main__":
    # Run on port 8080
    app.run(host="0.0.0.0", port=8080)