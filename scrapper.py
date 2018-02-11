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
        names = soup.find_all("h4", {"id": "productCardTitle"})  # name of listing
        info = soup.find_all("dl")  # contains price and desc
        time_ago = soup.find_all("time")
        hyperlinks = soup.find_all("a", {"id": "productCardThumbnail"})
        current_date = date.today()
        # process list of listings from page
        for n, i, t, h in zip(names, info, time_ago, hyperlinks):
            name = n.text
            x = i.find_all("dd")
            price_text = x[0].text
            price = float("".join(ele for ele in price_text if ele.isdigit()))
            desc = x[1].text
            # parse hyperlink
            hsplit = str(h).split(" ")
            for link in hsplit:
                if "href=" in link:
                    href = "https://carousell.com" + link[6:-1]
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
            if not acceptable_price["min"] < price < acceptable_price["max"]:
                valid = False
            # add listings to array
            if valid:
                data.append({"name": name, "price": price, "date": str(d), "link": href})
        return data

    except requests.exceptions.RequestException:
        print("Connection failed")


# generate additional smart labels based on common words in listing names
def generate_labels(data):
    # collect all words in given scope
    words = []
    labels = []
    for d in data:
        for w in d.name.split(" "):
            if w != "":
                words.append(w)

    # find word frequency
    word_frequency = {}
    for w1 in words:
        word_frequency[w1] = 0
        for w2 in words:
            if w1 == w2:
                word_frequency[w1] += 1
                words.remove(w1)

    max_return = 3  # number of labels to return
    for i in range(max_return):
        # returns highest frequency word as label
        top_word = max(word_frequency, key=lambda p: word_frequency[p])
        # print(word_frequency[top_word])
        if word_frequency[top_word] > 1:
            new_label = top_word.lower()
            labels.append(new_label)
            word_frequency.pop(top_word)
    if labels:
        return labels
    else:
        return None


def filter_results(filter_labels, data, tolerance=1):
    search_results = []
    temp_results = []
    for f in filter_labels:
        # if search_results empty, filtered results stored in search_results (effectively the first filter)
        if not search_results:
            for listing in data:
                # checks to see if label matches any word in name, to given tolerance, and returns results
                for word in listing.name.split(" "):
                    s = difflib.SequenceMatcher(None, f.lower(), word.lower())
                    if s.quick_ratio() >= tolerance or f.lower() in word.lower():
                        if listing not in search_results:
                            search_results.append(listing)

        # else, filtered results stored in temp_results for comparison
        else:
            for listing in data:
                # checks to see if label matches any word in name, to given tolerance, and returns results
                for word in listing.name.split(" "):
                    s = difflib.SequenceMatcher(None, f.lower(), word.lower())
                    if s.quick_ratio() >= tolerance or f.lower() in word.lower():
                        if listing not in temp_results:
                            temp_results.append(listing)

            # intersects all new search results
            search_results = list(filter(lambda x: x in search_results, temp_results))
            temp_results = []

    return search_results

# scrap("https://carousell.com/categories/electronics-7/audio-207/")
# generate_labels(data["sennheiser"])
# print(search_database(["sennheiser", "headphones"], [data["sennheiser"]]))


# df = pandas.DataFrame(data)
# df.to_csv("output.csv")