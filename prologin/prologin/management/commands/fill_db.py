# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone
from django.contrib.auth.models import User
from news.models import News
from team.models import Role, Team
from menu.models import MenuEntry
import datetime
import random

class LipsumWord():
    def __init__(self):
        self.lst = ['a', 'ac', 'accumsan', 'adipiscing', 'aenean', 'aliquam', 'aliquet', 'amet', 'ante', 'arcu', 'at', 'auctor', 'augue', 'bibendum', 'commodo', 'condimentum', 'congue', 'consectetur', 'consequat', 'convallis', 'cras', 'curabitur', 'cursus', 'dapibus', 'diam', 'dictum', 'dolor', 'donec', 'dui', 'duis', 'egestas', 'eget', 'eleifend', 'elementum', 'elit', 'enim', 'erat', 'eros', 'est', 'et', 'etiam', 'eu', 'euismod', 'fames', 'faucibus', 'felis', 'fermentum', 'feugiat', 'fringilla', 'fusce', 'gravida', 'habitant', 'hendrerit', 'iaculis', 'id', 'imperdiet', 'in', 'integer', 'interdum', 'ipsum', 'justo', 'lacinia', 'lacus', 'laoreet', 'lectus', 'libero', 'ligula', 'lobortis', 'lorem', 'luctus', 'maecenas', 'magna', 'malesuada', 'massa', 'mattis', 'mauris', 'metus', 'mi', 'molestie', 'mollis', 'morbi', 'nam', 'nec', 'neque', 'netus', 'nibh', 'nisi', 'nisl', 'non', 'nulla', 'nullam', 'nunc', 'odio', 'orci', 'ornare', 'pellentesque', 'pharetra', 'phasellus', 'placerat', 'porta', 'posuere', 'praesent', 'pretium', 'proin', 'pulvinar', 'purus', 'quam', 'quis', 'quisque', 'rhoncus', 'risus', 'rutrum', 'sagittis', 'sapien', 'scelerisque', 'sed', 'sem', 'semper', 'senectus', 'sit', 'sodales', 'suscipit', 'suspendisse', 'tellus', 'tempor', 'tempus', 'tincidunt', 'tortor', 'tristique', 'turpis', 'ultrices', 'ultricies', 'ut', 'varius', 'vehicula', 'vel', 'velit', 'venenatis', 'vestibulum', 'vitae', 'vivamus', 'viverra', 'volutpat', 'vulputate']
        self.word = random.sample(self.lst, 1)[0]

    def __str__(self):
        return self.word

class LipsumSentence():
    def __init__(self, min_words=3, max_words=15):
        self.str = ''
        for i in range(random.randint(min_words, max_words)):
            w = LipsumWord()
            self.str += ' ' if self.str != '' else ''
            self.str += str(w)
        self.str = self.str.capitalize() + '.'

    def __str__(self):
        return self.str

class LipsumParagraph():
    def __init__(self):
        self.str = ' '.join(str(LipsumSentence()) for _ in range(random.randint(3, 7)))

    def __str__(self):
        return self.str

class Command(BaseCommand):
    args = '<module module ...>'
    help = 'Fill the database for the specified modules.'

    def fill_users(self):
        User.objects.all().filter(is_superuser=False).delete()
        users = ['serialk', 'Tuxkowo', 'bakablue', 'epsilon012', 'Mareo', 'Zourp', 'kalenz', 'Horgix', 'Vic_Rattlehead', 'Artifère', 'davyg', 'Dettorer', 'pmderodat', 'Tycho', 'Zeletochoy', 'magicking', 'flutchman', 'nico', 'coucou747', 'Oxian', 'LLB', 'è_é']
        for name in users:
            email = name.lower() + '@prologin.org'
            User.objects.create_user(name, email, 'trolololo!!!').save()

    def fill_news(self):
        News.objects.all().delete()
        for i in range(42):
            title = str(LipsumSentence(max_words=6))
            body = ''
            for i in range(2):
                body += str(LipsumParagraph()) + ' '
            News(title=title, body=body).save()

    def fill_team(self):
        Team.objects.all().delete()
        Role.objects.all().delete()
        roles = {
            'Président': 1,
            'Membre persistant': 14,
            'Trésorier': 3,
            'Vice-Président': 2,
            'Responsable technique': 8,
            'Membre': 12,
            'Secrétaire': 4,
        }
        for name in roles:
            Role(rank=roles[name], role=name).save()
        for year in range(2010, 2015):
            for name in roles:
                r = Role.objects.all().filter(rank=roles[name])[0]
                u = User.objects.order_by('?')[0]
                Team(year=year, role=r, user=u).save()
            member = Role.objects.all().filter(rank=12)[0]
            for i in range(5):
                u = User.objects.order_by('?')[0]
                Team(year=year, role=member, user=u).save()

    def fill_menu(self):
        MenuEntry.objects.all().delete()
        entries = [
            {'name': 'Accueil', 'position': 1, 'url': 'home'},
            {'name': 'Prologin 2013', 'position': 2, 'url': '#'},
            {'name': 'Concours national', 'position': 3, 'url': '#'},
            {'name': 'Entraînement', 'position': 4, 'url': '#'},
            {'name': 'L\'association', 'position': 5, 'url': '#'},
            {'name': 'Forums', 'position': 6, 'url': '#'},
            {'name': 'Mon compte', 'position': 7, 'url': '#', 'access': 'logged'},
            {'name': 'Administrer', 'position': 21, 'url': '#', 'access': 'admin'},
            {'name': 'Se déconnecter', 'position': 42, 'url': '#', 'access': 'logged'},

            {'name': 'Questionnaire', 'parent': 2, 'position': 1, 'url': '#'},
            {'name': 'Demi-finales', 'parent': 2, 'position': 2, 'url': '#'},
            {'name': 'Finale', 'parent': 2, 'position': 3, 'url': '#'},
            {'name': 'Archives', 'parent': 2, 'position': 4, 'url': '#'},
            {'name': 'Album photo', 'parent': 2, 'position': 5, 'url': '#'},

            {'name': 'Documentation', 'parent': 3, 'position': 1, 'url': '#'},
            {'name': 'Manuel', 'parent': 3, 'position': 2, 'url': '#'},

            {'name': 'Historique', 'parent': 4, 'position': 1, 'url': '#'},
            {'name': 'L\'équipe', 'parent': 4, 'position': 2, 'url': 'team:index'},
        ]
        for entry in entries:
            e = MenuEntry(name=entry['name'], url=entry['url'], parent=None if 'parent' not in entry else entries[entry['parent']]['elem'], position=entry['position'], access='all' if 'access' not in entry else entry['access'])
            e.save()
            entry['elem'] = e

    def handle(self, *args, **options):
        modules = {
            'users': self.fill_users,
            'news': self.fill_news,
            'team': self.fill_team,
            'menu': self.fill_menu,
        }
        if len(args) < 1:
            self.stderr.write('Missing parameter.')
            return
        if args[0] == 'all':
            args = ['users', 'news', 'team', 'menu']
        for mod in args:
            if mod not in modules:
                raise CommandError('%s: unknown module' % mod)
            self.stdout.write('Loading data for module %s...' % mod)
            modules[mod]()