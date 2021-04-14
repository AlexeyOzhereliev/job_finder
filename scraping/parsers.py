import codecs
import requests
from bs4 import BeautifulSoup as BS
from random import randint

__all__ = ('hh', 'superjob', 'habr_job')

headers = [{'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:47.0) Gecko/20100101 Firefox/47.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*; q=0.8'},
           {'User-Agent': 'Opera/9.60 (Windows NT 6.0; U; en) Presto/2.1.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*; q=0.8'},
           {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*; q=0.8'},
           ]


def hh(url, city=None, language=None):
    """Осуществляет парсинг вакансий с сайта hh.ru"""
    jobs = []
    errors = []
    domain = 'https://hh.ru/'
    if url:
        resp = requests.get(url, headers=headers[randint(0, 2)])
        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            main_div = soup.find('div', attrs={'class': 'vacancy-serp'})
            if main_div:
                div_lst = main_div.find_all('div', attrs={'class': 'vacancy-serp-item'})
                for div in div_lst:
                    title = div.find('span', attrs={'class': 'g-user-content'})
                    href = title.a['href']
                    description = div.find('div', attrs={'class': 'g-user-content'})
                    descr_text = description.div.string
                    company = div.find('div', attrs={'class': 'vacancy-serp-item__meta-info-company'})
                    comp_a = company.a
                    if comp_a:
                        comp_text = comp_a.text
                    else:
                        comp_text = 'Наименование отсутсвует!'
                    jobs.append({'title': title.string, 'url': href,
                                 'description': descr_text, 'company': comp_text,
                                 'city_id': city, 'language_id': language})
            else:
                errors.append({'url': url, 'title': 'Div does not exists'})
        else:
            errors.append({'url': url, 'title': 'Page do not response'})

        return jobs, errors


def superjob(url, city=None, language=None):
    """Осуществляет парсинг вакансий с сайта superjob.ru"""
    jobs = []
    errors = []
    domain = 'https://www.superjob.ru/'
    if url:
        resp = requests.get(url, headers=headers[randint(0, 2)])
        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            main_div = soup.find_all('div', attrs={'class': '_3zucV undefined _3SGgo'})
            if main_div[1]:
                div_list = main_div[1].find_all('div', class_='Fo44F QiY08 LvoDO')
                for div in div_list:
                    title = div.find('div', attrs={'class': '_3mfro PlM3e _2JVkc _3LJqf'})
                    title_txt = title.a.text
                    href = title.a['href']
                    description_txt = div.find('span', class_='_3mfro _38T7m _9fXTd _2JVkc _2VHxz _15msI').text
                    company = div.find('span', class_='_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc '
                                                      '_2VHxz _15msI')
                    if company:
                        company = company.text

                    jobs.append({'title': title_txt, 'url': domain + href,
                                 'description': description_txt, 'company': company,
                                 'city_id': city, 'language_id': language})
            else:
                errors.append({'url': url, 'title': 'Div does not exists'})
        else:
            errors.append({'url': url, 'title': 'Page do not response'})

        return jobs, errors


def habr_job(url, city=None, language=None):
    """Осуществляет парсинг вакансий с сайта career.habr.com"""
    jobs = []
    errors = []
    domain = 'https://career.habr.com/'
    if url:
        resp = requests.get(url, headers=headers[randint(0, 2)])
        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            main_div = soup.find('div', class_='section-group section-group--gap-medium')
            if main_div:
                div_lst = main_div.find_all('div', class_='vacancy-card')
                for div in div_lst:
                    title = div.find('div', class_='vacancy-card__title')
                    title_txt = title.text
                    href = title.a['href']
                    description = div.find('div', class_='vacancy-card__skills').text
                    company = div.find('div', class_='vacancy-card__company-title').text
                    jobs.append({'title': title_txt, 'url': domain + href,
                                 'description': description, 'company': company,
                                 'city_id': city, 'language_id': language},
                                )
            else:
                errors.append({'url': url, 'title': 'Div does not exists'})
        else:
            errors.append({'url': url, 'title': 'Page do not response'})

        return jobs, errors




