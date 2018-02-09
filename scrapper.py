import requests
from bs4 import BeautifulSoup
import difflib
from datetime import date, timedelta


exception_words = ["spoilt", "broken", "1/10", "2/10", "3/10", "4/10"]
acceptable_price = {"min": 1, "max": 9999}


# query and collect listings for a given URL and returns an array with data
def scrap(url):
    try:
        data = []  # array to be returned
        # request data
        r = requests.get(url)
        c = r.content
        soup = BeautifulSoup(c, "html.parser")
        names = soup.find_all("h4", {"id": "productCardTitle"}) # name of listing
        info = soup.find_all("dl")  # contains price and desc
        time_ago = soup.find_all("time")
        current_date = date.today()
        # process list of listings from page
        for n, i, t in zip(names, info, time_ago):
            name = n.text
            x = i.find_all("dd")
            price = x[0].text
            desc = x[1].text
            # parse time ago data
            t_split = t.text.split(" ")
            if t_split[0] == "last":
                t_split[0] = "1"
            if "yesterday" in t_split[0]:
                d = current_date - timedelta(days=1)
            elif "year" in t_split[1]:
                d = date(current_date.year-int(t_split[0]), current_date.month, current_date.day)
            elif "month" in t_split[1]:
                if current_date.month <= int(t_split[0]):
                    d = date(current_date.year - 1, 12 - int(t_split[0]) + current_date.month, current_date.day)
                else:
                    d = date(current_date.year, current_date.month - int(t_split[0]), current_date.day)
            elif "day" in t_split[1]:
                d = current_date - timedelta(days=int(t_split[0]))
            else:
                d = current_date

            # filter listings with exception words
            valid = True
            for ex in exception_words:
                if ex in desc:
                    valid = False
            # filter listings with acceptable prices
            if not acceptable_price["min"] < float(price[2:].replace(",", "")) < acceptable_price["max"]:
                valid = False
            # add listings to array
            if valid:
                data.append({"name": name, "price": price, "date": str(d)})
        return data

    except requests.exceptions.RequestException:
        print("Connection failed")


# generate additional smart labels based on common words in listing names
def generate_labels(scope, scope_all = False):
    # collect all words in given scope
    words = []
    if scope_all:
        for subscope in scope:
            for ls in subscope:
                for w in ls["name"].split(" "):
                    words.append(w)
    else:
        for ls in scope:
            for w in ls["name"].split(" "):
                words.append(w)

    # find word frequency
    word_frequency = {}
    for w1 in words:
        word_frequency[w1] = 1
        for w2 in words:
            if w1 == w2:
                word_frequency[w1] += 1
                words.remove(w1)

    max_return = 3  # number of labels to return
    for i in range(max_return):
        top_word = max(word_frequency, key=word_frequency.get)  # returns highest frequency word as label
        word_frequency.pop(top_word)
        new_label = top_word.lower()
        if new_label not in labels:
            labels.append(new_label)


def search_database(lbs, scope, tolerance=1):
    search_results = []
    temp_results = []
    for label in lbs:
        if not search_results:  # stores search results of first label in search_results
            for subset in scope:
                for ls in subset:
                    # checks to see if label matches any word in name, to given tolerance, and returns results
                    for word in ls["name"].split(" "):
                        s = difflib.SequenceMatcher(None, label, word.lower())
                        if s.quick_ratio() >= tolerance:
                            if ls not in search_results:
                                search_results.append(ls)
        else:  # results of other label stored in temp_results for comparison
            for subset in scope:
                for ls in subset:
                    # checks to see if label matches any word in name, to given tolerance, and returns results
                    for word in ls["name"].split(" "):
                        s = difflib.SequenceMatcher(None, label, word.lower())
                        if s.quick_ratio() >= tolerance:
                            if ls not in temp_results:
                                temp_results.append(ls)

            search_results = list(filter(lambda x: x in search_results, temp_results))  # intersects all new search results
            temp_results = []
    return search_results


for i in scrap("https://carousell.com/categories/electronics-7/audio-207/?sort_by=&collection_id=207&cc_id=356"):
    print(i)
# generate_labels(data["sennheiser"])
# print(search_database(["sennheiser", "headphones"], [data["sennheiser"]]))


# df = pandas.DataFrame(data)
# df.to_csv("output.csv")