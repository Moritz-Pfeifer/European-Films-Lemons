from sqlite3 import Error
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime


language = 'en'
history_date = '04/09/2002'
base_url = f'https://www.cineuropa.org/'

history_date = datetime.strptime(history_date, '%d/%m/%Y')



def lovely_soup(url):
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'})
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
                                        review_author TEXT NULL,
                                        review_text TEXT NULL,
                                        review_date TEXT NULL,
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


def read_unfinished_from_db(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM reviews WHERE review_text IS NULL")
    rows = cur.fetchall()
    return rows


def insert_one(conn, url, title, review_author, review_date):
    conn.execute("INSERT INTO reviews (url, title, review_author, review_date) VALUES (?, ?, ?, ?);", (url, title, review_author, review_date))
    conn.commit()


def insert_two(conn, title, original_title, country, year, director, review_text):
    conn.execute(f'UPDATE reviews SET original_title = ?, country = ?, year = ?, director = ?, review_text = ? WHERE title = ?', (original_title, country, year, director, review_text, title))
    conn.commit()


def get_review_urls():
    review_urls = []

    for i in range(9999):
        url = f'{base_url}/{language}/freviews/p/{i+1}'
        soup = lovely_soup(url)
        for article in soup.select('div.article.latest'):
            title = article.select_one('p.news-info a span').text
            link = article.select_one('p.tag strong a')
            review_date = link.text
            review_author = article.select_one('p.news-info a').text.replace(title, '').split('by')[1].strip()

            if datetime.strptime(review_date, '%d/%m/%Y') <= history_date:
                return review_urls

            a = link['href']
            url = f'{base_url}{a}'
            print('part 1', title)
            insert_one(conn, url, title, review_author, review_date)


def get_review_data():
    reviews = read_unfinished_from_db(conn)

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

        print('part 2', review[2])
        insert_two(conn, review[2], original_title, country, year, director, all_texts.strip())


def main():
    get_review_urls()
    get_review_data()
    read_db(conn)


if __name__ == '__main__':
    main()
