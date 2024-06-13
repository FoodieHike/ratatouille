import os


from fastapi import HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


from admin import app
import schemas
import database


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))


directory = os.path.join(os.path.dirname(__file__), "static")

app.mount("/static", StaticFiles(directory=directory), name="static")


# эндпоинт для наполнения таблицы campaign
@app.post("/campaign/", response_model=schemas.Campaign)
async def create_campaign(campaign: schemas.CampaignCreate):
    new_campaign = await database.create_campaign(campaign)
    if new_campaign:
        return new_campaign
    raise HTTPException(status_code=404, detail='Not found')


@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse('main.html', {'request': request})
