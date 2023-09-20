import os

import zipfile

import requests

import pandas as pd
import csv

from typing import List

# =====================================================================


def nameGenerator():
    i = 0
    while 1:
        yield i
        i += 1


# generator of files names (counter from 0 to +inf)
namegen = nameGenerator()


def saveToTxt(data: List[str]):
    dirPath = '../static/parsingResults'
    # read items form list and add row to file
    with open(f'{dirPath}/parseData.txt', 'wt') as writer:
        for line in data:
            writer.write(line+'\n')


def saveToCsv(data: List[str]):
    dirPath = '../static/parsingResults'
    with open(f'{dirPath}/parseData.csv', 'w') as csvfile:

        csvwriter = csv.writer(csvfile, delimiter=';')

        # write headers
        csvwriter.writerow(('id', 'value'))

        # enumerate data to get id-value pairs
        enumdata = enumerate(data)
        csvwriter.writerows(enumdata)


def saveToExcel(data: List[str]):
    dirPath = '../static/parsingResults'
    # create data frame with 'value' column
    df = pd.DataFrame(columns=['value'])
    # create series from data
    s = pd.Series(data, name='value')
    # add series values to 'value' column of data frame
    df['value'] = s
    # rename index column
    df.index.name = 'id'

    df.to_excel(f'{dirPath}/parseData.xlsx')


def downloadImages(links: List[str]):
    global namegen

    dirPath = '../static/parsingResults/images'

    # check if folder os exists
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)
    else:
        # clear folder
        for file in os.scandir(dirPath):
            os.remove(file)

    # check if links is str and not list
    if not isinstance(links, list):
        links = [links]

    for l in links:
        try:
            # get content
            rawImage = requests.get(l)
            # open file and write content to the file
            with open(f'{dirPath}/{next(namegen)}.jpeg', 'wb') as handler:
                handler.write(rawImage.content)
        except Exception as e:
            print(e)

    with zipfile.ZipFile('../static/parsingResults/parsed_images.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in os.listdir(dirPath):
            zf.write(f'{dirPath}/{file}')

    namegen = nameGenerator()


def main():

    saveToTxt(data=list('a'*20))
    saveToCsv(data=list('a'*20))
    saveToExcel(data=list('a'*20))
    pass


if __name__ == '__main__':
    main()
