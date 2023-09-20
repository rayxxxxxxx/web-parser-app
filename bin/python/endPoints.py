
from fastapi import Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

import os
import shutil

import re

# =====================================================================

from main import *
import parser
import fileManager

# =====================================================================


# clear parsingResults folder before start parsing
@api.on_event(event_type='startup')
def clearFolders():
    shutil.rmtree(path='../static/parsingResults', ignore_errors=True)
    os.mkdir(path='../static/parsingResults')
    os.mkdir(path='../static/parsingResults/images')


@api.get(path='/index.html', response_class=HTMLResponse)
async def index(r: Request):
    context = {'request': r}

    for k in r.cookies:
        context[k] = r.cookies[k]

    return templates.TemplateResponse(name='index.html', context=context)


@api.get(path='/textResultViewer.html', response_class=HTMLResponse)
async def text(r: Request):
    context = {'request': r}

    for k in r.cookies:
        context[k] = r.cookies[k]

    return templates.TemplateResponse(name='textResultViewer.html', context=context)


@api.get(path='/imageResultViewer.html')
async def images(r: Request):
    context = {'request': r}

    for k in r.cookies:
        context[k] = r.cookies[k]

    return templates.TemplateResponse(name='imageResultViewer.html', context=context)


@api.post(path='/index.html/search', response_class=HTMLResponse)
async def search(r: Request):
    context = {'request': r}

    # get form data
    formItems = (await r.form()).items()
    formDict = dict(formItems)

    # set form data to context to remember inputs
    for k in formDict:
        context[k] = formDict[k]

    # add 'isScrollable' item if checkbox unchecked and set bool value (if it unchecked, it will not appear in form data)
    if 'isScrollable' not in formDict:
        formDict['isScrollable'] = False
    else:
        formDict['isScrollable'] = True

    # return to main page if have no URL
    if formDict['url'] == '':
        return RedirectResponse(url='/index.html', status_code=status.HTTP_303_SEE_OTHER)

    # preprocessing form data
    formDict = preprocessFormData(formDict)

    # define what data will be parsed to return corresponding HTML template
    whatToParse = 'text' if formDict['tag'] != 'img' else 'image'
    htmlTemplateName = 'textResultViewer.html' if formDict[
        'tag'] != 'img' else 'imageResultViewer.html'

    parser.scrollIterations = int(formDict['scrollIters'])
    parseResult = parser.parsingFunctions[whatToParse](
        formDict['url'],
        formDict['tag'],
        class_=formDict['class'],
        parentTag=formDict['parentTag'],
        parentClass=formDict['parentClass'],
        pagesQuantity=int(formDict['pagesQuantity']),
        scrollable=formDict['isScrollable'])

    parseResult = [x for x in parseResult if x != None]

    # save data to files
    fileManager.saveToTxt(parseResult)
    fileManager.saveToCsv(parseResult)
    fileManager.saveToExcel(parseResult)
    if whatToParse == 'image':
        fileManager.downloadImages(parseResult)

    # send parsed data in context to display on page
    context.update({'parseResult': parseResult})

    response = templates.TemplateResponse(
        name=htmlTemplateName, context=context)

    # cookies
    for key in formDict:
        response.set_cookie(key, formDict[key])

    return response


# =====================================================================


def preprocessFormData(fd: dict):
    for (k, v) in zip(fd.keys(), fd.values()):
        # if value is empty, suppose it could be any value
        if v == '':
            fd[k] = re.compile(r'.{,100}')
        # if tag has no such attribute
        elif v == 'none':
            fd[k] = None
    return fd


# =====================================================================
