from sqlite3 import Error
import sqlite3
import requests
from bs4 import BeautifulSoup
import datetime
import json
import urllib
import unidecode
import string
from colorama import Fore, Back, Style
import signal
import sys
from halo import Halo
from rotten_tomatoes_client import RottenTomatoesClient
import argparse
import os


def signal_handler(sig, frame):
    print(Style.RESET_ALL)
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


language = 'en'
history_date = '04/09/2002'


history_date = datetime.datetime.strptime(history_date, '%d/%m/%Y')


def lovely_soup(url):
    if 'rottentomatoes' in url:
        headers = {
            'Referer': 'https://www.rottentomatoes.com/m/notebook/reviews?type=user',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
    else:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'}

    r = requests.get(url, headers=headers)
    return BeautifulSoup(r.content, 'lxml')


def db_connect():
    try:
        conn = sqlite3.connect('data.db')
        create_table = """CREATE TABLE IF NOT EXISTS reviews (
                                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                        url TEXT NOT NULL,
                                        title TEXT NOT NULL,
                                        original_title TEXT NULL,
                                        director TEXT NULL,
                                        year TEXT NULL,
                                        country TEXT NULL,
                                        cineuropa_review_author TEXT NULL,
                                        cineuropa_review_text TEXT NULL,
                                        cineuropa_review_date TEXT NULL,
                                        variety_review_author TEXT NULL,
                                        variety_review_text TEXT NULL,
                                        variety_review_date TEXT NULL,
                                        hollywoodreporter_review_author TEXT NULL,
                                        hollywoodreporter_review_text TEXT NULL,
                                        hollywoodreporter_review_date TEXT NULL,
                                        screendaily_review_author TEXT NULL,
                                        screendaily_review_text TEXT NULL,
                                        screendaily_review_date TEXT NULL,
                                        rottentomatoes_tomatometer_score INTEGER NULL,
                                        rottentomatoes_audience_score INTEGER NULL,
                                        UNIQUE(title) ON CONFLICT IGNORE
                                        );"""
        conn.execute(create_table)
        return conn
    except Error as e:
        print(e)
    return None


conn = db_connect()


def read_db(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM reviews")
    rows = cur.fetchall()
    for row in rows:
        print(row)
        print()


def read_unfinished_hollywoodreporter_from_db(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM reviews WHERE hollywoodreporter_review_text IS NULL")
    rows = cur.fetchall()
    return rows


def read_unfinished_variety_from_db(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM reviews WHERE variety_review_text IS NULL AND director IS NOT NULL")
    rows = cur.fetchall()
    return rows


def read_unfinished_cineuropa_from_db(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM reviews WHERE cineuropa_review_text IS NULL")
    rows = cur.fetchall()
    return rows


def read_unfinished_screendaily_from_db(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM reviews WHERE screendaily_review_text IS NULL")
    rows = cur.fetchall()
    return rows


def read_unfinished_rottentomatoes_from_db(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM reviews WHERE rottentomatoes_tomatometer_score IS NULL")
    rows = cur.fetchall()
    return rows


def insert_cineuropa_one(conn, url, title, cineuropa_review_author, cineuropa_review_date):
    conn.execute("INSERT INTO reviews (url, title, cineuropa_review_author, cineuropa_review_date) VALUES (?, ?, ?, ?);", (url, title, cineuropa_review_author, cineuropa_review_date))
    conn.commit()


def insert_cineuropa_two(conn, title, original_title, country, year, director, cineuropa_review_text):
    conn.execute(f'UPDATE reviews SET original_title = ?, country = ?, year = ?, director = ?, cineuropa_review_text = ? WHERE title = ?',
                 (original_title, country, year, director, cineuropa_review_text, title))
    conn.commit()


def insert_variety_one(conn, variety_review_author, variety_review_date, variety_review_text, title):
    conn.execute(f'UPDATE reviews SET variety_review_author = ?, variety_review_date = ?, variety_review_text = ? WHERE title = ?',
                 (variety_review_author, variety_review_date, variety_review_text, title))
    conn.commit()


def insert_hollywoodreporter_one(conn, hollywoodreporter_review_author, hollywoodreporter_review_date, vhollywoodreporter_review_text, title):
    conn.execute(f'UPDATE reviews SET hollywoodreporter_review_author = ?, hollywoodreporter_review_date = ?, hollywoodreporter_review_text = ? WHERE title = ?',
                 (hollywoodreporter_review_author, hollywoodreporter_review_date, vhollywoodreporter_review_text, title))
    conn.commit()


def insert_screendaily_one(conn, screendaily_review_author, screendaily_review_date, screendaily_review_text, title):
    conn.execute(f'UPDATE reviews SET screendaily_review_author = ?, screendaily_review_date = ?, screendaily_review_text = ? WHERE title = ?',
                 (screendaily_review_author, screendaily_review_date, screendaily_review_text, title))
    conn.commit()


def insert_rottentomatoes_one(conn, rottentomatoes_tomatometer_score, rottentomatoes_audience_score, title):
    conn.execute(f'UPDATE reviews SET rottentomatoes_tomatometer_score = ?, rottentomatoes_audience_score = ? WHERE title = ?',
                 (rottentomatoes_tomatometer_score, rottentomatoes_audience_score, title))
    conn.commit()


def get_cineuropa_review_urls():
    with Halo(text='Gathering Cineuropa Urls', spinner='dots') as spinner:
        review_urls = []
        c = 0

        for i in range(9999):
            url = f'https://www.cineuropa.org/{language}/freviews/p/{i+1}'
            soup = lovely_soup(url)
            for article in soup.select('div.article.latest'):
                title = article.select_one('p.news-info a span').text
                link = article.select_one('p.tag strong a')
                cineuropa_review_date = link.text
                cineuropa_review_author = article.select_one('p.news-info a').text.replace(title, '').split('by')[1].strip()

                if datetime.datetime.strptime(cineuropa_review_date, '%d/%m/%Y') <= history_date:
                    return
                c += 1
                spinner.text = f'Gathering Cineuropa Urls ({c})'
                a = link['href']
                url = f'https://www.cineuropa.org/{a}'
                insert_cineuropa_one(conn, url, title, cineuropa_review_author, cineuropa_review_date)


def get_cineuropa_review_data():
    get_cineuropa_review_urls()
    reviews = read_unfinished_cineuropa_from_db(conn)

    for review in reviews:
        soup = lovely_soup(review[1])
        table = soup.select_one('table.scheda-film')
        for tr in table.select('tr'):
            if tr.select_one('td.title2c').text.lower() == 'original title: ':
                original_title = tr.select_one('td.contentc').text
            if tr.select_one('td.title2c').text.lower() == 'country: ':
                country = tr.select_one('td.contentc').text
            if tr.select_one('td.title2c').text.lower() == 'year: ':
                year = tr.select_one('td.contentc').text
            if tr.select_one('td.title2c').text.lower() == 'directed by: ':
                director = tr.select_one('td.contentc').text

        texts = soup.find('div', itemprop='text')
        all_texts = ''

        for p in texts.select('p'):
            col = p.find_parent('div')

            if '(translated from' not in p.text.lower() and not p.select('time'):
                all_texts += p.text.strip() + '\n\n'

        print(Fore.GREEN + f'Cineuropa - {review[2]}')
        insert_cineuropa_two(conn, review[2], original_title, country, year, director, all_texts.strip())


def get_variety_data(query_title, query_director):
    variety_headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en;q=0.8',
        'Connection': 'keep-alive',
        'Origin': 'https://variety.com',
        'Referer': 'https://variety.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }

    full_query = f'{query_title} {query_director}'

    json_data = {
        'engine_key': '1byyzyzxQM-Y595mXFkG',
        'page': 1,
        'q': full_query,
        'per_page': 100,
        'spelling': 'strict',
        'sort_direction': {
            'page': 'desc',
        },
        'sort_field': {
            'page': '_score',
        },
        # 'content_type': ['Article'],
        'filters': {
            "page": {
                # "content_type": "Article",
                "topics": {
                    "type": "and",
                    "values": [
                            "Reviews"
                    ]
                }
            }
        },
        'facets': {
            "page": [
                "topics",
                "tags",
                "author"
            ]
        },
    }

    data = requests.post('https://api.swiftype.com/api/v1/public/engines/search.json', headers=variety_headers, json=json_data).json()

    with open('data.json', 'w') as f:
        json.dump(data, f)

    for item in data['records']['page']:
        title = item['title'].translate(str.maketrans('', '', string.punctuation)).lower()
        query_title = query_title.translate(str.maketrans('', '', string.punctuation)).lower()
        if query_title in title:
            if query_director in item['body'].lower() or unidecode.unidecode(query_director) in item['body'].lower() or query_director in item['title'].lower() or unidecode.unidecode(query_director) in item['title'].lower():
                return {'title': item['title'],
                        'type': item['type'],
                        'body': item['body'],
                        'author': item['author'],
                        'date': datetime.datetime.strptime(item['published_at'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d/%m/%Y')}


def get_hollywoodreporter_data(query_title, query_director):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Connection': 'keep-alive',
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
        'Origin': 'https://www.hollywoodreporter.com',
        'Referer': 'https://www.hollywoodreporter.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }

    full_query = f'{query_title} {query_director}'

    json_data = {
        'engine_key': 'w7aP8_sUtCDsfqsCFYmc',
        'page': 1,
        'q': full_query,
        'per_page': 100,
        'spelling': 'strict',
        'sort_direction': {
            'page': 'desc',
        },
        'sort_field': {
            'page': '_score',
        },
        'facets': {
            'page': [
                'author',
                'tags',
                'topics',
            ],
        },
        'filters': {
            'page': {
                'topics': {
                    'type': 'and',
                    'values': [
                        'Movie Reviews',
                    ],
                },
            },
        },
    }

    data = requests.post('https://api.swiftype.com/api/v1/public/engines/search.json', headers=headers, json=json_data).json()

    for item in data['records']['page']:
        title = item['title'].translate(str.maketrans('', '', string.punctuation)).lower()
        query_title = query_title.translate(str.maketrans('', '', string.punctuation)).lower()
        if query_title in title:
            if query_director in item['body'].lower() or unidecode.unidecode(query_director) in item['body'].lower() or query_director in item['title'].lower() or unidecode.unidecode(query_director) in item['title'].lower():
                return {'title': item['title'],
                        'type': item['type'],
                        'body': item['body'],
                        'author': item['author'],
                        'date': datetime.datetime.strptime(item['published_at'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d/%m/%Y')}


def get_variety_review_data():
    rows = read_unfinished_variety_from_db(conn)

    for row in rows:
        title = row[2].lower()
        director = row[4].lower()

        review = get_variety_data(title, director)

        if review:
            insert_variety_one(conn, review['author'], review['date'], review['body'], row[2])
            print(Fore.GREEN + f'Variety - {title}')
        else:
            insert_variety_one(conn, 'NULL', 'NULL', 'NULL', row[2])
            print(Fore.RED + f'Variety - {title}')


def get_hollywoodreporter_review_data():
    rows = read_unfinished_hollywoodreporter_from_db(conn)

    for row in rows:
        title = row[2].lower()
        director = row[4].lower()
        review = get_hollywoodreporter_data(title, director)

        if review:
            author = review['author']
            if isinstance(author, list):
                author = ' '.join(review['author'])
            insert_hollywoodreporter_one(conn, author, review['date'], review['body'], row[2])
            print(Fore.GREEN + f'Hollywoodreporter - {title}')
        else:
            insert_hollywoodreporter_one(conn, 'NULL', 'NULL', 'NULL', row[2])
            print(Fore.RED + f'Hollywoodreporter - {title}')


def get_screendaily_data(title, director):
    ignore_me = ['Dir. ', 'Source: ', 'Dir/scr: ']
    query_string = urllib.parse.quote(f'{title}')
    url = f'https://www.screendaily.com/searchresults?qkeyword={query_string}&PageSize=10&parametrics=WVSECTIONCODE%7C2'
    soup = lovely_soup(url)

    items = soup.select_one('#content_sleeve').select('.listBlocks ul li')
    for item in items:
        all_texts = ''
        author = ''
        date = ''
        review_title = item.select_one('h3 a')
        if title.lower() in review_title.text.lower():
            url = review_title['href']
            soup = lovely_soup(url)
            if soup.select_one('span.author span.noLink'):
                author = soup.select_one('span.author span.noLink').text.strip()
            elif soup.select_one('span.author span.noLink'):
                author = soup.select_one('span.author a').text.split(',')[0].strip()

            date = soup.select('span.date')[0].text.strip()
            date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z').strftime('%d/%m/%Y')
            if soup.select_one('.factfile'):
                soup.select_one('.factfile').decompose()
            all = soup.select_one('.storytext')
            if all:
                if director in all.text or unidecode.unidecode(director) in all.text:
                    pss = soup.select('.storytext p')
                    ps = [i for i in pss if ignore_me not in i]
                    for p in ps:
                        all_texts += p.text.strip() + '\n\n'
                    return {'title': title,
                            'body': all_texts,
                            'author': author,
                            'date': date}


def get_screendaily_review_data():
    rows = read_unfinished_screendaily_from_db(conn)

    for row in rows:
        title = row[2]
        director = row[4]
        review = get_screendaily_data(title, director)

        if review:
            insert_screendaily_one(conn, review['author'], review['date'], review['body'], title)
            print(Fore.GREEN + f'Screendaily - {title}')
        else:
            insert_screendaily_one(conn, 'NULL', 'NULL', 'NULL', title)
            print(Fore.RED + f'Screendaily - {title}')


def get_rotten_tomatoes_data(title, year):
    params = {
        'searchQuery': f'{title} {year}',
        'type': 'movie',
        'f': 'null',
    }
    headers = {
        'Referer': 'https://www.rottentomatoes.com/m/notebook/reviews?type=user',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    try:
        r = requests.get('https://www.rottentomatoes.com/napi/search/all', headers=headers, params=params).json()
    except Exception as e:
        print(e)
        return False

    for movie in r['movie']['items']:
        tomatometer_score = 'NULL'
        audience_score = 'NULL'

        if unidecode.unidecode(title.lower()) in unidecode.unidecode(movie['name'].lower()):
            if year and movie['releaseYear'] in [str(int(year) - 1), year, str(int(year) + 1)]:

                if 'score' in movie['tomatometerScore']:
                    tomatometer_score = movie['tomatometerScore']['score']
                if 'score' in movie['audienceScore']:
                    audience_score = movie['audienceScore']['score']

        return {'ts': tomatometer_score, 'as': audience_score}


def get_rotten_tomatoes_review_data():
    rows = read_unfinished_rottentomatoes_from_db(conn)

    for row in rows:
        title = row[2]
        year = row[5]
        ts_var = None
        as_var = None
        score = get_rotten_tomatoes_data(title, year)
        if score and 'ts' in score and 'as' in score:
            if score['ts'] != 'NULL' or score['as'] != 'NULL':
                ts_var =  score['ts']
                as_var =  score['as']
                print(Fore.GREEN + f'Rotten Tomatoes - {title}')
        else:
            print(Fore.RED + f'Rotten Tomatoes - {title}')

        insert_rottentomatoes_one(conn, ts_var, as_var, title)


def if_args():
    no_args = True
    for arg in vars(args):
        if getattr(args, arg):
            no_args = True
            return no_args


def main():
    parser = argparse.ArgumentParser(description='Movie Analysis Fandango v1.0 (by u/impshum)')
    parser.add_argument(
        '-ce', '--cineuropa', help='Scrape Cineuropa Only', action='store_true')
    parser.add_argument(
        '-sd', '--screendaily', help='Scrape Screendaily Only', action='store_true')
    parser.add_argument(
        '-v', '--variety', help='Scrape Variety Only', action='store_true')
    parser.add_argument(
        '-hr', '--hollywood', help='Scrape Hollywoodreporter Only', action='store_true')
    parser.add_argument(
        '-rt', '--rotten', help='Scrape Rotten Tomatoes Only', action='store_true')
    parser.add_argument(
        '-all', '--all', help='Scrape All (leave args empty for the same result)', action='store_true')
    parser.add_argument(
        '-dd', '--deletedb', help='Delete Database (start fresh)', action='store_true')

    args = parser.parse_args()

    if args.cineuropa:
        print('learing Database')
        os.remove('data.db')
    elif args.cineuropa:
        print('Scraping Cineuropa Only')
        get_cineuropa_review_data()
    elif args.screendaily:
        print('Scraping Screendaily Only')
        get_screendaily_review_data()
    elif args.variety:
        print('Scraping Variety Only')
        get_variety_review_data()
    elif args.hollywood:
        print('Scraping Hollywoodreporter Only')
        get_hollywoodreporter_review_data()
    elif args.rotten:
        print('Scraping Rotten Tomatoes Only')
        get_rotten_tomatoes_review_data()
    else:
        print('Scraping All... Here we go again!')
        get_cineuropa_review_data()
        get_screendaily_review_data()
        get_variety_review_data()
        get_hollywoodreporter_review_data()
        get_rotten_tomatoes_review_data()

    print(Style.RESET_ALL)


if __name__ == '__main__':
    main()
