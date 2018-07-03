from flask import Flask, request, render_template
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from selenium import webdriver
from collections import defaultdict
from string import punctuation
from nltk.corpus import stopwords
from heapq import nlargest

stopwords = set(stopwords.words('english') + list(punctuation))
def compute_frequencies(word_sent):
    freq = defaultdict(int)
    for s in word_sent:
        for word in s:
            if word not in stopwords:
                freq[word] += 1
    m = float(max(freq.values()))
    for w in freq.keys():
        freq[w] = freq[w]/m
        if freq[w] >= 0.9 or freq[w] <= 0.1:
            freq[w] = 0
    freq = {k: v for k, v in freq.items() if v != 0}
    return freq

def summarize(text):
    sents = sent_tokenize(text)
    word_sent = [word_tokenize(s.lower()) for s in sents]
    freq = compute_frequencies(word_sent)

    ranking = defaultdict(int)
    for i, sentences in enumerate(word_sent):
        for w in sentences:
            if w in freq:
                ranking[i] += freq[w]

    sents_idx = nlargest(2, ranking, key=ranking.get)
    return [sents[j] for j in sents_idx]

def textParser(text):
    input = text
    if not text:
        return []
    if len(sent_tokenize(text)) > 2:
        input = " ".join(summarize(text))

    tokenized_text = nltk.tokenize.word_tokenize(input)
    tagged_text = nltk.pos_tag(tokenized_text)
    print(tagged_text)
    listOfWords = []
    tagsToIgnore = ['CC', 'CD', 'DT', 'IN', 'LS', 'TO', 'WDT', 'WP', 'WRB']
    for index, value in enumerate(tagged_text):
        if tagged_text[index - 1][1] == 'JJ' and (tagged_text[index][1] == 'NNS' or 'NN'):
            listOfWords[index - 1] = tagged_text[index - 1][0] + " " + tagged_text[index][0]
            listOfWords.append(" ")
        elif tagged_text[index][1] in tagsToIgnore:
            listOfWords.append(" ")
        else:
            listOfWords.append(tagged_text[index][0])
    unwanted = [" ", ".", ",", "!", '"', "'", "``", ':', '?', '(', ')', '[', ']', '{', '}', '<', '>']
    listOfWords = list(filter(lambda x: x not in unwanted, listOfWords))
    return listOfWords

def getImageAddress(listOfWords):
    # ChromeOptions allows us to control certain settings.
    options = webdriver.ChromeOptions()
    # Headless means that the browser won't open up when the code is run.
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.add_argument('headless')
    # Define the web-driver.
    driver = webdriver.Chrome(chrome_options=options)
    # Define a dictionary to store the image urls.
    image_urls = {}
    # Iterate through each word
    words = listOfWords
    for index, value in enumerate(words):
        # This handles multiple words.
        word_to_scrape = value.replace(" ", "%20")
        # Google the word
        driver.get("http://www.image-net.org/search?q=" + word_to_scrape)
        # driver.get("https://imgur.com/search?q=" + word_to_google)

        # Gather a list of image urls.
        images = driver.find_elements_by_tag_name('img')
        #images = driver.find_elements_by_css_selector("#gridMulti img")
        # Append the relevant urls to image_urls.

        for img in images:
            print(img.get_attribute('src'))
            if 'logo' not in img.get_attribute('src'):
                image_urls[value] = img.get_attribute('src')
                break

        if (value in image_urls) == False:
            driver.get("https://www.google.com/search?site=imghp&tbm=isch&source=hp&biw=1414&bih=709&q=" + word_to_scrape + "&oq=" + word_to_scrape)
            images = driver.find_elements_by_tag_name('img')
            for img in images:
                if isinstance(img.get_attribute('src'), str) and ('https://encrypted' in img.get_attribute('src')):
                    image_urls[value] = img.get_attribute('src')
                    break
        print(value in image_urls)
        if (value in image_urls) == False:
            driver.get("https://www.deviantart.com/?q=" + word_to_scrape)
            images = driver.find_elements_by_tag_name('img')
            for img in images:
                image_urls[value] = img.get_attribute('src')
                break

    driver.close()
    return image_urls

app = Flask(__name__)

@app.route('/')

def index():
    return render_template("main.html")

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    print(text)
    wordsToGoogle = textParser(text)
    print(wordsToGoogle)
    imageUrls = getImageAddress(wordsToGoogle)
    print(imageUrls)
    output = '<style> body { background-color: lightgrey; margin: 50px } div { border: 25px solid darkgrey; padding: 25px;}</style>'
    output += '<h1 align="center">' + text + '</h1>'
    output += '<div style = "background-color: white;">'
    for i in wordsToGoogle:
        output += '<h2>' + i + '</h2><img src=' + imageUrls[i] + '>'
    output += '</div>'
    return output

if __name__ == "__main__":
    app.run()