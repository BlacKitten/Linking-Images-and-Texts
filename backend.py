from selenium import webdriver
import nltk
import json
import time

'''
Input: a list of words.
Output: a dictionary of image links related to the input words.
'''
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
        word_to_google = value.replace(" ", "%20")
        # Google the word
        driver.get("https://www.google.com/search?site=imghp&tbm=isch&source=hp&biw=1414&bih=709&q=" + word_to_google + "&oq=" + word_to_google)
        # driver.get("https://imgur.com/search?q=" + word_to_google)

        # Gather a list of image urls.
        images = driver.find_elements_by_tag_name('img')
        #images = driver.find_elements_by_css_selector("#gridMulti img")
        # Append the relevant urls to image_urls.
        for img in images:
            if isinstance(img.get_attribute('src'), str) and ('https://encrypted' in img.get_attribute('src')):
                image_urls[value] = img.get_attribute('src')
                break
        print(value in image_urls)
        if (value in image_urls) == False:
            driver.get("https://www.deviantart.com/?q=" + word_to_google)
            images = driver.find_elements_by_tag_name('img')
            for img in images:
                image_urls[value] = img.get_attribute('src')
                break

    driver.close()
    return image_urls

'''
Input: String
Output: a list consisting of meaningful words or phrases
'''
def textParser(text):
    if not text:
        return []
    text = nltk.tokenize.word_tokenize(text)
    tagged_text = nltk.pos_tag(text)
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

def toJSON(imageUrls):
    filename = 'data.json'
    if filename:
        with open(filename, 'w') as f:
            json.dump(imageUrls, f)


if __name__ == "__main__":
    file = open("input.txt", "r")
    wordsToGoogle = textParser(file.read())
    print(wordsToGoogle)
    if wordsToGoogle:
        imageUrls = getImageAddress(wordsToGoogle)
        print(imageUrls)
        toJSON(imageUrls)
    else:
        print("Input is Empty.")