import hashlib
import requests
from django.conf import settings
from django.db import models
from django.core.cache import cache

from prologin.models import AddressableModel
from prologin.utils import upload_path


class ApprovedSchoolManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(approved=True)


class School(AddressableModel):
    def picture_upload_to(self, *args, **kwargs):
        return upload_path('school', using=lambda p: p.pk)(self, *args, **kwargs)

    name = models.CharField(max_length=128, blank=False, db_index=True)
    approved = models.BooleanField(default=False, db_index=True)

    # Optional fields
    imported = models.BooleanField(default=False, blank=True)
    uai = models.CharField(max_length=16, blank=True, null=True, db_index=True,
                           unique=True)
    acronym = models.CharField(max_length=32, blank=True)
    type = models.CharField(max_length=128, blank=True)
    academy = models.CharField(max_length=128, blank=True)

    objects = models.Manager()
    approved_schools = ApprovedSchoolManager()

    def edition_contestants(self, year):
        return self.contestants.filter(edition__year=year)

    @property
    def current_edition_contestants(self):
        return self.edition_contestants(settings.PROLOGIN_EDITION)

    @property
    def total_contestants_count(self):
        return self.contestants.count()

    @property
    def current_edition_contestants_count(self):
        return self.current_edition_contestants.count()

    @property
    def picture(self):
        try:
            return Facebook.search(self.name)[0]['picture']['data']['url']
        except (IndexError, KeyError):
            return None

    def clean(self):
        if self.uai == '':
            self.uai = None

    def __str__(self):
        if self.approved:
            return self.name
        else:
            return '(unapproved) %s' % self.name

    class Meta:
        ordering = ('approved', 'name')


class Facebook:
    params = {'access_token': settings.FACEBOOK_GRAPH_API_ACCESS_TOKEN,
              'fields': 'id,about,bio,category,description,general_info,link,name,website,picture',
              'format': 'json', 'pretty': '0'}

    @classmethod
    def _params(cls, **kwargs):
        p = cls.params.copy()
        p.update(kwargs)
        return p

    @classmethod
    def _request(cls, method, **kwargs):
        return requests.get('https://graph.facebook.com/v2.7' + method, params=cls._params(**kwargs), timeout=2).json()

    @classmethod
    def search(cls, query):
        query = query.strip().lower()
        if not query:
            return None

        def get_data():
            try:
                return [item for item in cls._request('/search', q=query, type='place')['data']
                        if item.get('category') in ('School', 'University')]
            except Exception:
                return []

        key = hashlib.sha1(query.encode('utf8', 'replace')).hexdigest()
        return cache.get_or_set('schools/search/' + key, get_data, 60 * 60 * 24)

    @classmethod
    def get(cls, id):
        def get_data():
            try:
                return cls._request('/' + id)
            except Exception:
                return None

        key = hashlib.sha1(id.encode('utf8', 'replace')).hexdigest()
        return cache.get_or_set('schools/id/' + key, get_data, 60 * 60 * 24)
