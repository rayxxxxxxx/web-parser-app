import re
from typing import List

import requests
from bs4 import BeautifulSoup

from selenium import webdriver

import time

# =====================================================================

import fileManager

# =====================================================================


def prettifyString(s):
    if (
            s != None and s.text.strip() != '\n' and s.text.strip() != ''):
        return s.text.strip()


def fixURL(url):
    # if there is no part with http(s): then add it to beginning of url
    if re.search(r'http[s]{0,1}:', url) == None:
        return 'http:'+url
    else:
        return url


def validateURL(url):
    # dont need url, where file extension .gif or have no http:// part
    if (not re.search(r'/.gif', url) or not re.search(r'http://', url)):
        return True
    return False


def getPageSource(url: str):
    global scrollIterations

    # create driver
    driver = webdriver.Firefox()
    driver.minimize_window()
    driver.get(url)

    for i in range(scrollIterations):
        # scroll page to bottom
        driver.execute_script(
            f'window.scrollTo(1, document.body.scrollHeight)')
        print(
            f"scrolling process: [{i+1} out of {scrollIterations}]")
        time.sleep(2)

    # save page for BS4 parsing
    with open('../static/parsingResults/parsePageSource.html', 'w') as handler:
        handler.write(driver.page_source)

    driver.close()

    # return page source text
    return open('../static/parsingResults/parsePageSource.html', 'r').read()


def parseText(url: str, tag: str, class_=re.compile(r'.{,100}'), parentTag: str = re.compile(r'.{,100}'), parentClass: str = re.compile(r'.{,100}'), pagesQuantity: int = 1, scrollable: bool = False) -> List[str]:
    # split url to get part where page number is changing (item with index 1, middle)
    urlParts = url.split('`')
    # join all part to single url
    urlStr = ''.join(urlParts)

    # if there is no ` sign in url, then pages template wasn't defined, so need to parse only one page
    if len(urlParts) == 1:
        pagesQuantity = 1

    res = []
    for i in range(1, pagesQuantity+1):
        # increment page number
        if len(urlParts) != 1:
            urlParts[1] = str(int(urlParts[1])+1)
            urlStr = ''.join(urlParts)

        # if page is scrollable then firstly scroll page down and get source text
        if scrollable:
            parseData = getPageSource(urlStr)
        else:
            # get content from url
            parseData = requests.get(urlStr).text

        # create BS4 object
        soup = BeautifulSoup(parseData, 'html.parser')

        parseResult = []
        # if parent tag is defined, than firstly finding all elements with parent tag and class
        if parentTag != None:
            parseResult = soup.find_all(parentTag, class_=parentClass)
            # after getting elements with parentTag, searching in result items by tag and/or class
            parseResult = [x.find(tag, class_=class_) for x in parseResult]
        else:
            parseResult = soup.find_all(tag, class_=class_)

        # push found data to list
        res.extend(list(map(prettifyString, parseResult)))

    return res


def parseImage(url: str, tag: str, class_=re.compile(r'.{,100}'), parentTag: str = re.compile(r'.{,100}'), parentClass: str = re.compile(r'.{,100}'), pagesQuantity: int = 1, scrollable: bool = False) -> List[str]:
    # split url to get part where page number is changing (item with index 1, middle)
    urlParts = url.split('`')
    # join all part to single url
    urlStr = ''.join(urlParts)

    # if there is no ` sign in url, then pages template wasn't defined, so need to parse only one page
    if len(urlParts) == 1:
        pagesQuantity = 1

    # list of links from all searched pages
    links = []
    for i in range(1, pagesQuantity+1):
        currLinks = []

        # increment page number
        if len(urlParts) != 1:
            urlParts[1] = str(int(urlParts[1])+1)
            urlStr = ''.join(urlParts)

        # if page is scrollable then firstly scroll page down and get source text
        if scrollable:
            parseData = getPageSource(urlStr)
        else:
            # get content from url
            parseData = requests.get(urlStr).text
            # parseData = open(
            #     'static/parsingResults/parsePageSource.html', 'r').read()

        soup = BeautifulSoup(parseData, 'html.parser')

        parseResult = []
        # if parent tag is defined, than firstly finding all elements with parent tag and class
        if parentTag != None:
            parseResult = soup.find_all(parentTag, class_=parentClass)
            # after getting elements with parentTag, searching in result items by tag and/or class
            parseResult = [x.find(tag, class_=class_) for x in parseResult]
            # exclude all None values
            parseResult = [x for x in parseResult if x != None]
        else:
            parseResult = soup.find_all(tag, class_=class_)

        # not all <img> contain proper src attribute
        # here for all results trying to find attribute with 'src' part
        for res in parseResult:
            for attr in res.attrs:
                # if attribute has 'src' part
                if re.search(r'src', attr) != None or re.search(r'data', attr):
                    if res.attrs[attr] == '':
                        continue

                    appendData = res[attr[0] if isinstance(
                        attr, list) else attr]

                    currLinks.append(
                        appendData[-1] if isinstance(appendData, list) else appendData)
                    break

        # fixing urls if have no http: part
        currLinks = list(map(fixURL, currLinks))
        # remove broken links
        currLinks = list(filter(validateURL, currLinks))
        links.extend(currLinks)

    return links


# ====================================================================


scrollIterations = 10

parsingFunctions = {'text': parseText, 'image': parseImage}


# ====================================================================


def main():
    textUrl = f'https://www.reddit.com/r/pics'

    ParentTag_text = 'div'
    ParentClass_text = '_2SdHzo12ISmrC8H86TgSCp'

    Tag_text = 'h3'
    Class_text = re.compile(r'.{,100}')

    texts = parseText(
        textUrl, Tag_text, class_=Class_text, parentTag=ParentTag_text, parentClass=ParentClass_text, pagesQuantity=1, scrollable=True)

    fileManager.saveToCsv(texts)

    imageUrl = f'https://joyreactor.cc/tag/art/new/`20000`'

    ParentTag_img = 'div'
    ParentClass_img = 'image'

    Tag_img = 'img'
    Class_img = None

    images = parseImage(
        imageUrl, Tag_img, class_=Class_img, parentTag=ParentTag_img, parentClass=ParentClass_img, pagesQuantity=1, scrollable=True)

    fileManager.saveToTxt(images)
    fileManager.saveToExcel(images)
    fileManager.downloadImages(images[:2])


if __name__ == '__main__':
    main()
