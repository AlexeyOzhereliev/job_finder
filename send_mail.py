import os, sys
import datetime
import django
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model

proj = os.path.dirname(os.path.abspath('manage.py'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'scraping_service.settings'

django.setup()
from scraping.models import Vacancy, Error, Url, City, Language
from scraping_service.settings import EMAIL_HOST_USER

ADMIN = EMAIL_HOST_USER
today = datetime.date.today()
empty = '<h2>К сожалению по Вашим предпочтениям данных нет.</h2>'
subject = f'Рассылка вакансий за {today}'
text_content = 'Сервис рассылки вакансий'
from_email = EMAIL_HOST_USER

User = get_user_model()
qs = User.objects.filter(send_email=True).values('city', 'language', 'email')
users_dct = {}
for i in qs:
    users_dct.setdefault((i['city'], i['language']), [])
    users_dct[(i['city'], i['language'])].append(i['email'])
if users_dct:
    params = {'city_id__in': [], 'language_id__in': []}
    for pair in users_dct.keys():
        params['city_id__in'].append(pair[0])
        params['language_id__in'].append(pair[1])
    qs = Vacancy.objects.filter(**params, timestamp=today).values()
    vacancies = {}
    for i in qs:
        vacancies.setdefault((i['city_id'], i['language_id']), [])
        vacancies[(i['city_id'], i['language_id'])].append(i)
    for keys, emails in users_dct.items():
        rows = vacancies.get(keys, [])
        html = ''
        for row in rows:
            html += f'<h5><a href="{row["url"]}">{row["title"]}</a></h5>'
            html += f'<p>{row["description"]}</p>'
            html += f'<p>{row["company"]}</p><br><hr>'
        _html = html if html else empty
        for email in emails:
            to = email
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(_html, "text/html")
            msg.send()

qs = Error.objects.filter(timestamp=today)
subject = ''
text_content = ''
to = ADMIN
_html = ''
if qs.exists():
    error = qs.first()
    data = error.data.get('errors', [])
    for i in data:
        _html += f'<p><a href="{i["url"]}">Error: {i["title"]}</a></p>'
    subject += f'Ошибки скраппинга {today}'
    text_content += 'Ошибки скраппинга'
    data = error.data.get('user_data', [])
    if data:
        for i in data:
            _html += '<hr>'
            _html += '<h2>Пожелания пользователя</h2>'
            _html += f'<p>Город: {i["city"]}, Язык программирования: {i["language"]}</p>'
        subject += f' Пожелания пользователей {today}'
        text_content += ' Пожелания пользователей'


qs = Url.objects.all().values('city', 'language')
urls_errors = ''
urls_dct = {(i['city'], i['language']): True for i in qs}
for key in users_dct.keys():
    if key not in urls_dct:
        urls_errors += f'<p>Для города: {key[0]} и  языка {key[1]} отсутсвуют урлы.</a><br>'

if urls_errors:
    subject += 'Отсутсвующие урлы'
    _html += urls_errors

if subject:
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(_html, "text/html")
    msg.send()
