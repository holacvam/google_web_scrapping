#!/usr/bin/env python
# encoding: utf-8

import urllib
import requests
from bs4 import BeautifulSoup
import re
import logging as log
import pandas as pd
log = log.getLogger('google_search')
links, titles, text, domain, url, domains = ([] for i in range(6))


def get_response(query, number_result=20):
    enquery = urllib.parse.quote_plus(query)
    google_url = "https://www.google.com/search?q=" + enquery + "&num=" + str(number_result)
    response = requests.get(google_url, {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'})
    result = BeautifulSoup(response.text, "html.parser").find_all('div', attrs={'class': 'ZINbbc'})
    return result, query.replace("'", "")


def result_parser(result):
    for r in result[0]:
        try:
            link, title = r.find('a', href=True), r.find('div', attrs={'class': 'vvjwJb'}).get_text()
            description, domain = r.find('div', attrs={'class': 's3v9rd'}).get_text(), r.find('div', attrs={'class': 'UPmit'}).get_text()
            if link != '' and title != '' and description != '':
                links.append(link['href'])
                titles.append(title)
                text.append(description)
                domains.append(domain)
        except:
            continue

    final_links = [re.search('\/url\?q\=(.*)\&sa', l).group(1) if re.search('\/url\?q\=(.*)\&sa', l) is not None else l for l in links]
    final_domains = [d.split()[0].split("//")[1] if 'https://' in d else d for d in domains]
    df = pd.DataFrame(
        {'title': titles,
         'text': text,
         'url': final_links,
         'domain': final_domains
         })
    df['keyword'] = result[1]
    df['Position'] = df.index + 1
    df = df[['keyword', 'Position', 'title', 'text', 'url', 'domain']]
    return df


if __name__ == "__main__":
    try:
        od = dict()
        for n, i in enumerate(list(pd.read_excel('input.xlsx')['Keywords'].unique()), start=1):
            print("Running for " + i)
            od[n] = result_parser(get_response(i))
        df_final = pd.concat([i for i in list(od.values())])
        df_final.to_excel('output.xlsx', index=False)
        log.info("Google search has been completed and excel is generated")
    except Exception as e:
        log.error("Error while Google Search due to " + str(e))
        raise e



