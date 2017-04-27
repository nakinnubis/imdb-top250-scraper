# IMDB Top 250 Scraper

### About

Script to scrape IMDB Top 250 list of movies and store scraped data in chosen format (json, csv, sqlite). Scraped data includes basic information like movie title, imdb top 250 position, genre, story, cast, director, language, country, duration in minutes.

### Requirements

Script is tested with python 3.5.2 version.

#### Aditional Python Libraries

- [lxml](https://github.com/lxml/lxml/)
- [requests](https://github.com/kennethreitz/requests)

### Installation

```
git clone https://github.com/fuzzy69/imdb-top250-scraper.git
cd imdb-top250-scraper/
virtualenv -p /usr/bin/python3 env
. env/bin/activate
pip install -r requirements.txt
```

### Usage

```
python main.py [ARGUMENTS]

```
Optional arguments

```
-c C        Number of items to scrape (min 1, max 250)
-d D        Delay between requests in seconds
-f F        Output file
-ft FT      Output file format (json, csv, sqlite)
-t T        Thread count
-p P        Use proxies from file (max threads <= proxies count)
-mp         Download movie posters
```
Example:

```
python main.py -c 100 -t 2 -mp -f results -ft json
```
Using this command script will scrape 100 movies with 2 threads, save results in data/results.json and movie posters in data/* as jpg images.

### TODO

- save results to sqlite
- proxies