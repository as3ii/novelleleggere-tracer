#!/usr/bin/env python3

from sys import exit
import os

def load_from_file(file_name):
    from json import load
    from os.path import isfile

    if not isfile(file_name):
        return dict()

    with open(file_name) as jfile:
        return load(jfile)


def print_queries(queries):
    for search in queries.items():
        print("\nsearch: ", search[0])
        for query_url in search[1]:
            print("query url:", query_url)
            for url in search[1].items():
                for result in url[1].items():
                    print("\n", result[1].get('title'), ":", result[1].get('date'))
                    print(" ", result[0])


def refresh(queries, dbfile, token, chatid):
    for search in queries.items():
        for _ in search[1]:
            queries = run_query(search[0], queries, dbfile, token, chatid)
    return queries


def delete(to_delete, queries):
    queries.pop(to_delete)
    return queries


def run_query(name, queries, dbfile, token, chatid):
    import telegram
    import requests
    from bs4 import BeautifulSoup
    import time

    url = "https://www.novelleleggere.com/category/" + name.replace(" ", "-").lower()
    print("running query - ", name, url)
    # get page
    try:
        page = requests.get(url)
    except requests.exceptions.ConnectionError:
        exit("Connection Error")
    soup = BeautifulSoup(page.text, "html.parser")
    # extract title and url
    chapter_list = soup.find(class_="fusion-posts-container")
    chapter_list_items = chapter_list.find_all("h2")

    msg = []

    for chapter in reversed(chapter_list_items):
        item = chapter.find_all("a")
        title = item[0].contents[0]
        link = item[0].get("href")

        if title.lower().find("spoiler") != -1 or \
            title.lower().find("non editato") != -1:
            continue

        if not queries.get(name):   # insert the new traced novel
            print("\nNew traced novel added: ", name)
            date = time.strftime("%d/%m/%Y", time.localtime(time.time()))
            print("Adding result: ", title, " - ", date)
            tmp = "New element found for **"+name+"**: __"+title+"__\n"
            tmp += "\n"+link
            msg.append(tmp)
            queries[name] = {url: {link: {"title": title, "date": date}}}
        else:
            if not queries.get(name).get(url).get(link):    #found a new element
                print("Adding result: ", title, " - ", date)
                tmp = "New element found for **"+name+"**: __"+title+"__\n"
                tmp += "\n"+link
                msg.append(tmp)
                date = time.strftime("%d/%m/%Y", time.localtime(time.time()))
                queries[name][url][link] = {"title": title, "date": date}

    if msg:
        # initialize bot
        bot = telegram.Bot(token,
                request=telegram.utils.request.Request(read_timeout=60))

        count = 0   # counter for antispam protection
        while len(msg) > 0:
            bot.send_message(chat_id=chatid, text=msg[0], parse_mode="markdown",
                    disable_web_page_preview=True)
            del msg[0]
            count = count + 1
            if count >= 10:
                count = 0
                print("sleeping for 30 seconds to avoid hitting", end=' ')
                print("telegram flood protection")
                time.sleep(30)

        save(dbfile, queries)
        return queries


def save(file_name, queries):
    from json import dumps
    with open(file_name, 'w') as filej:
        filej.write(dumps(queries))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", dest="name",
            metavar="\"novel name\"",
            help="name of the novel to trace")
    parser.add_argument("-d", "--dele", dest="dele",
            metavar="\"novel name\"",
            help="name of the novel you don't want to trace anymore")
    parser.add_argument("-r", "--refresh", dest="refresh",
            action="store_true", default=False,
            help="refresh tracker results")
    parser.add_argument("-l", "--list", dest="list",
            action="store_true", default=False,
            help="print a list of current traced novel")
    parser.add_argument("-t", "--token", dest="token",
            metavar="123456789:ASDFG-5asdf5asdfasdsdf4_sdf54asf", default=None,
            help="bot token")
    parser.add_argument("-c", "--chatid", dest="chatid",
            metavar="123456789", default=None,
            help="chat id")
    parser.add_argument("-b", "--db", dest="dbfile",
            metavar="\"/path/to/dbfile.json\"", default="novelleleggere.json",
            help="path to the file used as database")
    args = parser.parse_args()

    if args.token is not None:
        token = args.token
    else:
        token = os.environ.get('TOKEN')
        if token is None:
            raise RuntimeError("TOKEN environment variable not set")

    if args.chatid is not None:
        chatid = args.chatid
    else:
        chatid = os.environ.get('CHATID')
        if chatid is None:
            raise RuntimeError("CHATID environment variable not set")

    dbfile = os.environ.get('DBFILE')
    if dbfile is None:
        dbfile = args.dbfile


    queries = load_from_file(dbfile)

    if args.list:
        print("printing current status...")
        print_queries(queries)

    if args.name is not None:
        queries = run_query(args.name, queries, dbfile, token, chatid)

    if args.refresh:
        queries = refresh(queries, dbfile, token, chatid)

    if args.dele is not None:
        queries = delete(args.dele, queries)

    print()
    save(dbfile, queries)

