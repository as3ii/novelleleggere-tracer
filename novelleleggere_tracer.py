#!/usr/bin/env python3

import argparse
import json
import os.path
import time
import sys
import telegram_send
import requests
from bs4 import BeautifulSoup

PARSER = argparse.ArgumentParser()
PARSER.add_argument("--name", dest="name", metavar="\"novel name\"", help="name of the novel to trace")
PARSER.add_argument("--dele", dest="dele", metavar="\"novel name\"", help="name of the novel you don't want to trace anymore")
PARSER.add_argument("-r", "--refresh", dest="refresh", action="store_true", help="refresh tracker results")
PARSER.set_defaults(refresh=False)
PARSER.add_argument("-l", "--list", dest="list", action="store_true", help="print a list of current traced novel")
PARSER.set_defaults(list=False)

ARGS = PARSER.parse_args()

QUERIES = dict()
DBFILE = "novel.traced"


def load_from_file(file_name):
    global QUERIES
    if not os.path.isfile(file_name):
        return

    with open(file_name) as file:
        QUERIES = json.load(file)



def print_queries():
    global QUERIES
    #print(queries, "\n\n")
    for search in QUERIES.items():
        print("\nsearch: ", search[0])
        for query_url in search[1]:
            print("query url:", query_url)
            for url in search[1].items():
                for result in url[1].items():
                    print("\n", result[1].get('title'), ":", result[1].get('date'))
                    print(" ", result[0])


def refresh():
    global QUERIES
    for search in QUERIES.items():
        for _ in search[1]:
            run_query(search[0])


def delete(to_delete):
    global QUERIES
    QUERIES.pop(to_delete)


def run_query(name):
    url = "https://www.novelleleggere.com/category/" + name.replace(" ", "-").lower()
    print("running query - ", name, url)
    global QUERIES
    # get page
    try:
        page = requests.get(url)
    except requests.exceptions.ConnectionError:
        sys.exit("Connection Error")
    soup = BeautifulSoup(page.text, "html.parser")
    # extract title and url
    chapter_list = soup.find(class_="fusion-posts-container")
    chapter_list_items = chapter_list.find_all("h2")

    msg = []

    for chapter in reversed(chapter_list_items):
        item = chapter.find_all("a")
        title = item[0].contents[0]
        link = item[0].get("href")

        if title.lower().find("spoiler") != -1:
            continue

        if not QUERIES.get(name):   # insert the new traced novel
            date = time.strftime("%d/%m/%Y", time.localtime(time.time()))
            QUERIES[name] = {url: {link: {"title": title, "date": date}}}
            print("\nNew traced novel added: ", name)
            print("Adding result: ", title, " - ", date)
        else:   # add traced novel to dictionary
            if not QUERIES.get(name).get(url).get(link):    #found a new element
                tmp = "New element found for **"+name+"**: __"+title+"__\n"
                tmp += "\n"+link
                msg.append(tmp)
                date = time.strftime("%d/%m/%Y", time.localtime(time.time()))
                QUERIES[name][url][link] = {"title": title, "date": date}
    if msg:
        while len(msg) != 0:
            to_be_sent = msg[:20]
            telegram_send.send(messages=to_be_sent, parse_mode="markdown",
                    disable_web_page_preview=True, timeout=60)
            del msg[:20]
            if len(to_be_sent) == 20:
                print("sleeping for one minute to avoid hitting telegram flood protection")
                time.sleep(60)
        print("\n --- --- --- \n".join(msg).replace("**", "").replace("__", ""))
        save(DBFILE)
    # print("queries file saved: ", queries)



def save(file_name):
    with open(file_name, 'w') as file:
        file.write(json.dumps(QUERIES))



if __name__ == '__main__':

    load_from_file(DBFILE)

    if ARGS.list:
        print("printing current status...")
        print_queries()

    if ARGS.name is not None:
        run_query(ARGS.name)

    if ARGS.refresh:
        refresh()

    if ARGS.dele is not None:
        delete(ARGS.dele)

    print()
    save(DBFILE)
