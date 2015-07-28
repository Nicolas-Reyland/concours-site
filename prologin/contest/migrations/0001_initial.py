# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

import prologin.models
import contest.models


class Migration(migrations.Migration):

    dependencies = [
        ('centers', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contestant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shirt_size', prologin.models.EnumField(contest.models.Contestant.ShirtSize, null=True, blank=True, choices=[(0, 'XS'), (1, 'S'), (2, 'M'), (3, 'L'), (4, 'XL'), (5, 'XXL')], db_index=True)),
                ('preferred_language', prologin.models.CodingLanguageField(null=True, choices=[('ada', 'Ada'), ('brainfuck', 'Brainfuck'), ('c', 'C'), ('csharp', 'C#'), ('cpp', 'C++'), ('fsharp', 'F#'), ('haskell', 'Haskell'), ('java', 'Java'), ('js', 'Javascript'), ('lua', 'Lua'), ('ocaml', 'OCaml'), ('pascal', 'Pascal'), ('perl', 'Perl'), ('php', 'PHP'), ('pseudocode', 'Pseudocode'), ('python2', 'Python 2'), ('python3', 'Python 3'), ('scheme', 'Scheme'), ('vb', 'VB')], verbose_name='Coding language', max_length=64, blank=True, db_index=True)),
                ('correction_comments', models.TextField(blank=True)),
                ('score_qualif_qcm', models.IntegerField(verbose_name='QCM score', null=True, blank=True)),
                ('score_qualif_algo', models.IntegerField(verbose_name='Algo exercises score', null=True, blank=True)),
                ('score_qualif_bonus', models.IntegerField(verbose_name='Bonus score', null=True, blank=True)),
                ('score_semifinal_written', models.IntegerField(verbose_name='Written exam score', null=True, blank=True)),
                ('score_semifinal_interview', models.IntegerField(verbose_name='Interview score', null=True, blank=True)),
                ('score_semifinal_machine', models.IntegerField(verbose_name='Machine exam score', null=True, blank=True)),
                ('score_semifinal_bonus', models.IntegerField(verbose_name='Bonus score', null=True, blank=True)),
                ('score_final', models.IntegerField(verbose_name='Score', null=True, blank=True)),
                ('score_final_bonus', models.IntegerField(verbose_name='Bonus score', null=True, blank=True)),
                ('correction_by', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='corrections', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Edition',
            fields=[
                ('year', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('date_begin', models.DateTimeField()),
                ('date_end', models.DateTimeField()),
            ],
            options={
                'ordering': ('-year',),
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', prologin.models.EnumField(contest.models.Event.Type, choices=[(0, 'Qualification'), (1, 'Semifinal'), (2, 'Final')], db_index=True)),
                ('date_begin', models.DateField(null=True, blank=True)),
                ('date_end', models.DateField(null=True, blank=True)),
                ('center', models.ForeignKey(null=True, to='centers.Center', related_name='events', blank=True)),
                ('edition', models.ForeignKey(related_name='events', to='contest.Edition')),
            ],
        ),
        migrations.CreateModel(
            name='EventWish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('contestant', models.ForeignKey(to='contest.Contestant')),
                ('event', models.ForeignKey(to='contest.Event')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='contestant',
            name='edition',
            field=models.ForeignKey(related_name='contestants', to='contest.Edition'),
        ),
        migrations.AddField(
            model_name='contestant',
            name='event_wishes',
            field=models.ManyToManyField(through='contest.EventWish', related_name='applicants', to='contest.Event'),
        ),
        migrations.AddField(
            model_name='contestant',
            name='user',
            field=models.ForeignKey(related_name='contestants', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='contestant',
            unique_together={('user', 'edition')},
        ),
    ]