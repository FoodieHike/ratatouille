from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


import models
import new_db_tests


# Создаем приложение и интегрируем к нему фласк админскую приложуху
app = FastAPI()

templates = Jinja2Templates(directory='templates')

app.mount("/static", StaticFiles(directory="static"), name="static")


# эндпоинт для наполнения таблицы campaign
@app.post("/campaign/", response_model=models.Campaign)
async def create_campaign(campaign: models.CampaignCreate):
    new_campaign = await new_db_tests.create_campaign(campaign)
    if new_campaign:
        return new_campaign
    raise HTTPException(status_code=404, detail='Not found')


@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse('main.html', {'request': request})


@app.get('/admin/')
async def admin(request: Request):
    return templates.TemplateResponse(
        'fastapi_index.html', {'request': request}
    )
