# Cineuropa Scraper

Scrapes reviews from Cineuropa, and checks Variety, Hollywood Reporter and Screen Daily for corresponding reviews. Then downloads them into a sqlite db.

### Instructions

-   Install requirements `pip install -r requirements.txt`
-   Edit the `history_date` variable to your liking.
-   Run it `python run.py`

### Arguments

    usage: run.py [-h] [-ce] [-sd] [-v] [-hr] [-rt] [-all] [-dd]

    Movie Analysis Fandango v1.0 (by u/impshum)

    optional arguments:
      -h, --help          show this help message and exit
      -ce, --cineuropa    Scrape Cineuropa Only
      -sd, --screendaily  Scrape Screendaily Only
      -v, --variety       Scrape Variety Only
      -hr, --hollywood    Scrape Hollywoodreporter Only
      -rt, --rotten       Scrape Rotten Tomatoes Only
      -all, --all         Scrape All (leave args empty for the same result)
      -dd, --deletedb     Delete Database (start fresh)