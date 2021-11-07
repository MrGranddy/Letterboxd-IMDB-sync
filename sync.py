import typing
import requests
import re

from bs4 import BeautifulSoup


def imdb_read_ratings_private(csv_path: str) -> typing.Dict[str, int]:

    # Read the users rating data exported from IMDB
    with open(csv_path, "r") as f:
        next(f)
        data = [line.strip().split(",") for line in f]

    # Dictionary to hold user's rating data
    rating_dict: dict[str, int] = {}

    # Create rating dictionary from the raw data
    for data_row in data:

        # Get movie title
        movie_title = data_row[3]

        # Get user's rating
        rating = int(data_row[1])

        # Get and add year
        year_match = re.search("([0-9]{4})", rating_dict[8])
        if year_match != None:
            movie_title = movie_title + ("|||%s" % year_match.group(1))

        rating_dict[movie_title] = rating

    # Rating dictionary is in the format "{MOVIE_TITLE}|||{YEAR}" -> RATING
    return rating_dict


def imdb_read_ratings_public(user_id: str) -> typing.Dict[str, int]:

    # User rating page
    user_rating_url = "https://www.imdb.com/user/" + user_id + "/ratings"
    headers = {"Accept-Language": "en-US,en;q=0.5"}

    # Dictionary to hold user's rating data
    rating_dict: dict[str, int] = {}

    # Get page html and parse with bs4
    response = requests.get(user_rating_url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")

    while True:  # Pagination loop

        movie_items_list = soup.find_all("div", {"class": "lister-item mode-detail"})

        for movie in movie_items_list:

            # Get movie title
            movie_header = movie.find("h3", {"class", "lister-item-header"})
            movie_title = movie_header.find("a").text

            # Get user's rating
            user_rating_div = movie.find(
                "div", {"class", "ipl-rating-star ipl-rating-star--other-user small"}
            )
            rating = int(
                user_rating_div.find("span", {"class", "ipl-rating-star__rating"}).text
            )

            # Get and add year
            year_span = movie.find(
                "span", {"class": "lister-item-year text-muted unbold"}
            )
            if year_span != None:
                year_match = re.search("([0-9]{4})", year_span.text)
                if year_match != None:
                    movie_title = movie_title + ("|||%s" % year_match.group(1))

            rating_dict[movie_title] = rating

        # Parse next page if it exists else break
        next_page = soup.find("a", {"class": "flat-button lister-page-next next-page"})
        if next_page == None:
            break
        else:
            next_page_url = "https://www.imdb.com" + next_page["href"]
            response = requests.get(next_page_url, headers=headers)
            soup = BeautifulSoup(response.content, "lxml")

    # Rating dictionary is in the format "{MOVIE_TITLE}|||{YEAR}" -> RATING
    return rating_dict


print(len(imdb_read_ratings_public("ur111248677")))

# print( imdb_read_ratings_private("ratings.csv") )
# print( imdb_read_ratings_public("ur111248677") )
