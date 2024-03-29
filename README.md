GoogolCrawler
=============
![GitHub Release Date](https://img.shields.io/github/release-date/googolsearch/googolcrawler) ![GitHub commit activity](https://img.shields.io/github/commit-activity/w/googolsearch/googolcrawler) ![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/googolsearch/googolcrawler/total) ![GitHub Release](https://img.shields.io/github/v/release/googolsearch/googolcrawler) ![GitHub forks](https://img.shields.io/github/forks/googolsearch/googolcrawler) 


> Note: GoogolCrawler is designed for the Googol developers, and is not particularly user friendly.
> There may also be bugs/glitches in GoogolCralwer, we are not responsible for any loss of data.

GoogolCrawler is the web crawler used by the Googol Search Engine to find new pages to index.

## Requirements

GoogolCrawler requires:
 - Python 3
 - nltk
 - requests
 - BeautilfulSoup4
 - SQLite3 (Included with Python)
 - [WaybackProxy](https://github.com/richardg867/WaybackProxy)

## Usage
Start WaybackProxy on port `7000` and set the date to `20030101` or any other date you wish to crawl.

After WaybackProxy has started, configure GoogolCrawler to use the urls desired, and run the script.
> Note: More URLs = More Threads. Only add what your machine can handle.
> By default, GoogolCrawler will use 22 URLs, which means 22 threads, though this is not a limit/minimum.

> Note: If you have a fresh install of NLTK, you may need to install `stopwords` and `tokenize`.

GoogolCrawler will write all output data to `data.db`, an SQLite3 database.

Here is an example of one row of data created by GoogolCrawler:
|id | url                        | title      | tags               |
|---|----------------------------|------------|--------------------|
| 3 | http://www.google.com      | Google     | web, search, tools |

> Note: Tags are not HTML tags, they are the top 3 most common words on a page

> Note: The table's name is `GlobalData`

If you wanted to, for example, do a search for `Google`, you could use this SQL query:

`SELECT * FROM GlobalData WHERE title LIKE "%Google%" OR tags LIKE "%Google%"`
