#!/usr/bin/env python3.7

import argparse
import json
import os.path
import time
import telegram_send
import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("--name", dest="name", metavar="\"novel name\"", help="name of the novel to trace")
parser.add_argument("--dele", metavar="\"novel name\"", help="name of the novel you don't want to trace anymore")
parser.add_argument("-r", "--refresh", dest="refresh", action="store_true", help="refresh tracker results")
parser.set_defaults(refresh=False)
parser.add_argument("-l", "--list", dest="list", action="store_true", help="print a list of current traced novel")
parser.set_defaults(list=False)

args = parser.parse_args()

queries = dict()
dbFile = "novel.traced"


def load_from_file(fileName):
    global queries
    if not os.path.isfile(fileName):
        return

    with open(fileName) as file:
        queries = json.load(file)



def print_queries():
    global queries
    #print(queries, "\n\n")
    for search in queries.items():
        print("\nsearch: ", search[0])
        for query_url in search[1]:
            print("query url:", query_url)
            for url in search[1].items():
                for result in url[1].items():
                    print("\n", result[1].get('title'), ":", result[1].get('date'))
                    print(" ", result[0])


def refresh():
    global queries
    for search in queries.items():
        for query_url in search[1]:
            run_query(search[0])


def delete(toDelete):
    global queries
    queries.pop(toDelete)


def run_query(name):
    url = "https://www.novelleleggere.com/category/" + name.replace(" ", "-").lower()
    print("running query - ", name, url)
    global queries
    # get page
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    # extract title and url
    chapter_list = soup.find(class_="fusion-posts-container")
    chapter_list_items = chapter_list.find_all("h2")

    msg = []

    for chapter in reversed(chapter_list_items):
        item = chapter.find_all("a")
        title = item[0].contents[0]
        link = item[0].get("href")

        if title.lower().find("spoiler") == -1:
            continue

        if not queries.get(name):   # insert the new traced novel
            date = time.strftime("%d/%m/%Y", time.localtime(time.time()))
            queries[name] = {url: {link: {"title": title, "date": date}}}
            print("\nNew traced novel added: ", name)
            print("Adding result: ", title, " - ", date)
        else:   # add traced novel to dictionary
            if not queries.get(name).get(url).get(link):    #found a new element
                tmp = "New element found for **"+name+"**: __"+title+"__\n"
                tmp += "\n"+link
                msg.append(tmp)
                date = time.strftime("%d/%m/%Y", time.localtime(time.time()))
                queries[name][url][link] = {"title": title, "date": date}
    if len(msg) > 0:
        telegram_send.send(messages=msg, parse_mode="markdown", disable_web_page_preview=True, timeout=60)
        print("\n --- --- --- \n".join(msg).replace("**", "").replace("__", ""))
        save(dbFile)
    # print("queries file saved: ", queries)



def save(fileName):
    with open(fileName, 'w') as file:
        file.write(json.dumps(queries))



if __name__ == '__main__':

    load_from_file(dbFile)

    if args.list:
        print("printing current status...")
        print_queries()

    if args.name is not None:
        run_query(args.name)

    if args.refresh:
        refresh()

    if args.dele is not None:
        delete(args.delete)

    print()
    save(dbFile)

