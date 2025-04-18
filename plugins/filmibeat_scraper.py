import requests
from bs4 import BeautifulSoup
import logging

def fetch_filmibeat_ott_releases():
    url = "https://www.filmibeat.com/top-listing/ott-movie-releases-this-week/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                      " (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    logging.info("Filmibeat page fetched successfully.")
    logging.info(f"Sample HTML: {soup.prettify()[:1000]}")  # Preview first 1000 chars

    movie_cards = soup.select(".movie-top-listing")  # May need to update this selector
    releases = []

    for card in movie_cards:
        title_tag = card.select_one(".movie-title")
        platform_tag = card.select_one(".ott-name")
        date_tag = card.select_one(".ott-release-date")
        img_tag = card.select_one("img")

        if not title_tag or not platform_tag or not date_tag or not img_tag:
            continue

        movie = {
            "title": title_tag.get_text(strip=True),
            "platform": platform_tag.get_text(strip=True),
            "release_date": date_tag.get_text(strip=True),
            "poster_url": img_tag["data-src"] if img_tag.has_attr("data-src") else img_tag["src"]
        }
        releases.append(movie)

    return releases
