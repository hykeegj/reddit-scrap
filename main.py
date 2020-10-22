import requests
from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup

"""
When you try to scrape reddit make sure to send the 'headers' on your request.
Reddit blocks scrappers so we have to include these headers to make reddit think
that we are a normal computer and not a python script.
How to use: requests.get(url, headers=headers)
"""

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}


"""
All subreddits have the same url:
i.e : https://reddit.com/r/javascript
You can add more subreddits to the list, just make sure they exist.
To make a request, use this url:
https://www.reddit.com/r/{subreddit}/top/?t=month
This will give you the top posts in per month.
"""

subreddits = [
    "javascript",
    "reactjs",
    "reactnative",
    "programming",
    "css",
    "golang",
    "flutter",
    "rust",
    "django"
]


app = Flask("DayEleven")


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/read')
def read():
    db = {}
    all_subreddit_list = []
    temp_subreddit_list = []
    all_href_list = []
    all_title_list = []
    all_vote_list = []

    for subreddit in subreddits:
        if request.args.get(subreddit) == None:
            continue
        elif request.args.get(subreddit) == "on":
            subreddit_list = []
            vote_list = []
            title_list = []
            href_list = []

            url = f"https://www.reddit.com/r/{subreddit}/top/?t=month"
            html = requests.get(url, headers=headers).text
            soup = BeautifulSoup(html, "lxml")
            vote = soup.find_all(
                "div", {"class": "_1rZYMD_4xY3gRcSS3p8ODO _25IkBM0rRUqWX5ZojEMAFQ"})

            for item in vote:
                vote_list.append(item.get_text())
                subreddit_list.append(subreddit)
            # del vote_list[1]
            # del subreddit_list[1]

            for num, _ in enumerate(vote_list):
                if vote_list[num][-1] == 'k':
                    vote_list[num] = str(
                        int(float(vote_list[num][0:-1]) * 1000))
                else:
                    continue

            title = soup.find_all("div", class_="_1poyrkZ7g36PawDueRza-J")

            for item in title:
                item = item.find("h3", class_="_eYtD2XCVieq6emjKBH3m")
                title_list.append(item.get_text())
            # del title_list[1]

            for item in title:
                item = item.find("a", class_="SQnoC3ObvgnGjWt90zD9Z")
                href_list.append(item)

            # del href_list[1]

            for subreddit, href, title, vote in zip(subreddit_list, href_list, title_list, vote_list):
                if subreddit == None or href == None or title == None or vote == None:
                    subreddit_list.remove(subreddit)
                    href_list.remove(href)
                    title_list.remove(title)
                    vote_list.remove(vote)
                else:
                    continue

            for num, _ in enumerate(href_list):
                href_list[num] = f"https://www.reddit.com{href_list[num].get('href')}"

            all_subreddit_list.extend(subreddit_list)
            all_href_list.extend(href_list)
            all_title_list.extend(title_list)
            all_vote_list.extend(vote_list)
            temp_subreddit_list.append(subreddit)
        else:
            redirect('/')
            return
    for vote, subreddit, href, title in zip(all_vote_list, all_subreddit_list, all_href_list, all_title_list):
        db[int(vote)] = {
            'subreddit': subreddit,
            'href': href,
            'title': title,
            'vote': int(vote)
        }
    db = sorted(db.items(), reverse=True)

    return render_template("read.html", db=db, enumerate=enumerate, temp_subreddit_list=temp_subreddit_list, subreddit_list=all_subreddit_list, href_list=all_href_list, title_list=all_title_list, vote_list=all_vote_list, zip=zip)


app.run()
