import random
import requests
from bs4 import BeautifulSoup

COMMON_WORDS = set("the be to of and a in that have I it for not on with he as you do at this but his by from they we say her she or an will my one all would there their what so up out if about who get which go me when make can like time no just him know take people into year your good some could them see other than then now look only come its over think also back after use two how our work first well way even new want because any these give day most us".split())

def get_random_link_from_url(url):
    soup = BeautifulSoup(requests.get(url).text)
    anchors = soup.find_all(attrs={"class": "menu"})[0].find_all("a")
    random.shuffle(anchors)
    for anchor in anchors:
        href = anchor.get("href")
        if href.startswith("http://"):
            print "RANDOM LINK:", href
            return href

def get_book_link_from_url(url):
    soup = BeautifulSoup(requests.get(url).text)
    anchors = soup.find_all('a')
    random.shuffle(anchors)
    for anchor in anchors:
        href = anchor.get("href")
        if "buy-ebook" in href:
            continue
        if href.startswith("http"):
            continue
        if "javascript" in href:
            continue
        if "#" in href:
            continue
        if 'cart' in href:
            continue
        return "http://buy-ebook.com/" + href

def paginate_category(url):
    soup = BeautifulSoup(requests.get(url).text)
    for table in reversed(soup.find_all("table")):
        if "More results" in table.get_text():
            res = random.choice(table.find_all("a")).get("href")
            print "paging to", res
            return res
    print "Giving up on page, just using first page"
    return url


def get_book_page():
    book_href = get_book_link_from_url(paginate_category(get_random_link_from_url("http://buy-ebook.com")))
    print "CRAWLING", book_href
    soup = BeautifulSoup(requests.get(book_href).text)

    return text_with_newlines(soup.body)


def text_with_newlines(elem):
    text = ''
    for e in elem.recursiveChildGenerator():
        if isinstance(e, basestring):
            text += e.strip()
        elif e.name == 'br':
            text += '\n'
        else:
            if not (text.endswith(" ")):
                text += ' '
    return text


def read_file_as_string():
    in_file = open("input.txt", 'r')
    full_string = ""
    started = False
    for line in in_file:
        if started:
            if line.startswith("***"):
                return full_string
            full_string += line
        else:
            if line.startswith("_"):
                started = True
    return None

def pos_tagged(text):
    return requests.post("http://text-processing.com/api/tag/", dict(text=text.lower())).json()['text']

boring_blacklist = "money tips buy price book now xxx 20 page download day home learn refund contact credit purchase wait chapter risk"
starting_blacklist = "to and but overr"
pos_trailing_blacklist = "RB WHT IN TO DT CC PRP PRP$ VB VBD VBN VBZ JJ"
pos_anywhere_blacklist = "LS"
def is_boring(text):
    lowered = text.strip().lower()
    if len(lowered.split()) < 3:
        return True
    for word in boring_blacklist.split():
        if word in lowered:
            print "Too boring: (%s)" % word, text
            return True

    for word in starting_blacklist.split():
        if lowered.startswith(word + ' '):
            print 'started with', word, ':', text
            return True

    tagged = pos_tagged(text).strip()
    if "CD" in tagged:
        print "contains number:", text
        return True

    for pos in pos_trailing_blacklist.split():
        if tagged.endswith('/' + pos + ')'):
            print 'ended with POS', pos, ':', text
            return True

    for pos in pos_anywhere_blacklist.split():
        if ('/' + pos) in tagged:
            print 'contained POS', pos, ':', text
            return True

    if lowered.count('.') + lowered.count(',') + lowered.count('!') > 1:
        print 'Too much punctuation', lowered
        return True

    for word in lowered.split():
        if word not in COMMON_WORDS:
            return False
    print 'had all common words:', text
    return True

def extract_substring_of_words(in_text):
    words = in_text.split()
    start = random.randint(0, len(words))
    tweet = ""
    for i in range(100):
        if start + i >= len(words):
            return tweet
        new_tweet = tweet + ' ' + words[start + i]
        if len(new_tweet) > 80:
            return tweet
        if i > 3 and (random.random() < 0.1):
            return tweet
        if tweet.strip().endswith("."):
            if random.random() < 0.9:
                print 'stopping at a period'
                return tweet
            else:
                print "ended with a period, but fuck it"
        tweet = new_tweet
    print 'giving up'

blacklist = "login refund arts category $ { } < > account mailman risk taken"

def contains_bad_word(line):
    lowered = line.lower()
    for word in blacklist.split():
        if word in lowered:
            return True
    return False

def version_two(in_text):
    good_lines = []
    for line in in_text.split('\n'):
        if len(line) < 140:
            continue
        if line.strip() is '':
            continue
        if contains_bad_word(line):
            continue
        good_lines.append(line)

    print "FOUND", len(good_lines), "GOOD LINES"
    random.shuffle(good_lines)
    for line in good_lines:
        for i in range(5):
            extracted = extract_substring_of_words(line)
            if is_boring(extracted):
                continue
            print "extracting from", line
            extracted = extracted.replace('"', "")
            extracted = extracted.replace("-", " ")
            extracted = extracted.strip()
            if extracted.endswith('.') and random.random() < 0.9:
                print 'killing the last period.'
                extracted = extracted[:-1]
            return extracted

def crawl():
    try:
        return version_two(get_book_page())
    except Exception:
        return None

if __name__ == "__main__":
    output = version_two(get_book_page())
    print '\n\n========================='
    print output
