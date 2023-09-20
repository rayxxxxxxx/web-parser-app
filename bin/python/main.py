import uvicorn

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI

import webbrowser

# =====================================================================

from endPoints import *

# =====================================================================


api = FastAPI()
api.mount('/static', StaticFiles(directory='../static'), name='static')
templates = Jinja2Templates(directory='../html_templates')


# =====================================================================


app = 'main:api'
host = '127.0.0.1'
port = 8888
reload = True

mainurl = f'http://{host}:{port}/index.html'


def main():

    print(
        f'======================================================================================================')
    print(
        f':::::::::::::::::::::::::::::::::: {mainurl} ::::::::::::::::::::::::::::::::::')
    print(
        f'======================================================================================================')

    webbrowser.open(url=mainurl)

    uvicorn.run(app, host=host, port=port, reload=reload)


if __name__ == '__main__':
    main()
