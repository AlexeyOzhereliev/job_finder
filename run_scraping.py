import asyncio
import codecs
import os, sys
import datetime as dt
from django.contrib.auth import get_user_model
from django.db import DatabaseError

proj = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(proj)
os.environ['DJANGO_SETTINGS_MODULE'] = 'scraping_service.settings'

import django

django.setup()

from scraping.parsers import *
from scraping.models import Vacancy, Error, Url

User = get_user_model()

parsers = (
    (hh, 'hh'),
    (superjob, 'superjob'),
    (habr_job, 'habr_job')
)

jobs, errors = [], []


def get_settings():
    """"Возвращает набор id города и id языка программирования юзеров, подписанных на рассылку"""
    qs_settings = User.objects.filter(send_email=True).values()
    settings_lst = set((q['city_id'], q['language_id']) for q in qs_settings)
    return settings_lst


def get_urls(_settings):
    """Возвращает список словарей, в каждом из которых содержатся значения
    языка программировани, города и связанный с ними URL """
    qs_urls = Url.objects.all().values()
    url_dct = {(q['city_id'], q['language_id']): q['url_data'] for q in qs_urls}
    urls = []
    for pair in _settings:
        if pair in url_dct:
            tmp = {}
            tmp['city'] = pair[0]
            tmp['language'] = pair[1]
            tmp['url_data'] = url_dct[pair]
            urls.append(tmp)
    return urls


async def main(value):
    """Запускает функции парсинга и производит запись, полученных данных
    данных в списки jobs и errors"""
    func, url, city, language = value
    job, err = await loop.run_in_executor(None, func, url, city, language)
    errors.extend(err)
    jobs.extend(job)

settings = get_settings()
url_list = get_urls(settings)

loop = asyncio.get_event_loop()
tmp_tasks = [(func, data['url_data'][key], data['city'], data['language'])
             for data in url_list
             for func, key in parsers]
tasks = asyncio.wait([loop.create_task(main(f)) for f in tmp_tasks])

loop.run_until_complete(tasks)
loop.close()

old_vacancy = Vacancy.objects.all()
old_vacancy.delete()

for job in jobs:
    v = Vacancy(**job)
    try:
        v.save()
    except DatabaseError:
        pass

if errors:
    qs_errors = Error.objects.filter(timestamp=dt.date.today())
    if qs_errors.exists():
        err = qs_errors.first()
        err.data.update({'errors': errors})
        err.save()
    else:
        er = Error(data=f'errors: {errors}').save()

