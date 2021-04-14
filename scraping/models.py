import jsonfield
from django.db import models
from .utils import get_converted_from_cyrillic_to_latin


def default_urls():
    return {'hh': '', 'superjob': '', 'habr_job': ''}


class City(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название населеного пункта",
                            unique=True)
    slug = models.CharField(max_length=50, blank=True, unique=True)

    class Meta:
        verbose_name = 'Название населеного пункта'
        verbose_name_plural = "Название населенных пунктов"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_converted_from_cyrillic_to_latin(str(self.name))
        super().save(*args, **kwargs)


class Language(models.Model):
    name = models.CharField(max_length=50, verbose_name="Язык программирования",
                            unique=True)
    slug = models.CharField(max_length=50, blank=True, unique=True)

    class Meta:
        verbose_name = 'Язык программирования'
        verbose_name_plural = "Языки программирования"

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=250, verbose_name='Вакансия')
    company = models.CharField(max_length=250, verbose_name='Компания')
    description = models.TextField(verbose_name='Описание вакансии')
    city = models.ForeignKey('City', on_delete=models.CASCADE, verbose_name='Населенный пункт')
    language = models.ForeignKey('Language', on_delete=models.CASCADE, verbose_name='Язык программирования')
    timestamp = models.DateField(verbose_name='Дата добавления', auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = "Вакансии"
        ordering = ['-timestamp']

    def __str__(self):
        return self.title


class Error(models.Model):
    timestamp = models.DateField(verbose_name='Дата добавления', auto_now_add=True)
    data = models.JSONField()

    def __str__(self):
        return str(self.timestamp)


class Url(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Населенный пункт')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, verbose_name='Язык программирования')
    url_data = models.JSONField(default=default_urls)

    class Meta:
        unique_together = ('city', 'language')
