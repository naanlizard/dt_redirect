# dt\_redirect

This small python script creates a webserver running on port 8080 that forwards
users to the latest discussion thread on /r/neoliberal. The logic is rather
simple -- the bot simply looks for the latest thread titled "Discussion Thread"
posted by the user "jobautomator". Since these values are hardcoded, if there's
any change to the DT, this script must also be updated.

In case no DT is found, users are redirected to the subreddit itself.

I've also included the associated NGINX configuration file.

Supports the following trailing arguments in the URL path

/dt/stream - returns a reddit-stream.com url

/dt/old - returns old.reddit.com instead of www

---

To run in docker: `docker compose up -d --build` (remove `-d` if you don't want to fork it to the background)