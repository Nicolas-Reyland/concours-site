from centers.models import Center
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from ordered_model.models import OrderedModel
from prologin.utils import ChoiceEnum


class Edition(models.Model):
    year = models.PositiveIntegerField(db_index=True)
    date_begin = models.DateTimeField()
    date_end = models.DateTimeField()

    class Meta:
        ordering = ('-year',)

    @property
    def is_current(self):
        return self.date_begin <= timezone.now() <= self.date_end

    def __str__(self):
        return "Prologin {}".format(self.year)


class Event(models.Model):
    class EventType(ChoiceEnum):
        qualification = 0
        regionale = 1
        finale = 2

    edition = models.ForeignKey(Edition, related_name='events')
    center = models.ForeignKey(Center, blank=True, null=True, related_name='events')
    type = models.SmallIntegerField(choices=EventType.choices(), db_index=True)
    date_begin = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)

    def __str__(self):
        return "{edition}: {type} starting {starting}{at}".format(
            edition=self.edition,
            type=self.get_type_display(),
            starting=self.date_begin,
            at=" at %s" % self.center if self.center else "",
        )


class Contestant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contestants')
    edition = models.ForeignKey(Edition, related_name='contestants')
    event_wishes = models.ManyToManyField(Event, through='EventWish', related_name='applicants')

    correction_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='corrections')
    correction_comments = models.TextField(blank=True)

    score_qualif_qcm = models.IntegerField(blank=True, null=True, verbose_name=_("QCM score"))
    score_qualif_algo = models.IntegerField(blank=True, null=True, verbose_name=_("Algo exercises score"))
    score_qualif_bonus = models.IntegerField(blank=True, null=True, verbose_name=_("Bonus score"))
    score_regionale_written = models.IntegerField(blank=True, null=True, verbose_name=_("Written exam score"))
    score_regionale_interview = models.IntegerField(blank=True, null=True, verbose_name=_("Interview score"))
    score_regionale_machine = models.IntegerField(blank=True, null=True, verbose_name=_("Machine exam score"))
    score_regionale_bonus = models.IntegerField(blank=True, null=True, verbose_name=_("Bonus score"))
    score_finale = models.IntegerField(blank=True, null=True, verbose_name=_("Score"))
    score_finale_bonus = models.IntegerField(blank=True, null=True, verbose_name=_("Bonus score"))

    class Meta:
        unique_together = ('user', 'edition')

    @property
    def total_score(self):
        return sum(getattr(self, name) or 0
                   for name in self._meta.get_all_field_names()
                   if name.startswith('score_'))

    @property
    def approved_wishes(self):
        return EventWish.objects.select_related('event').filter(contestant=self, is_approved=True)

    def __str__(self):
        return "{edition}: {user}".format(user=self.user, edition=self.edition)


class EventWish(OrderedModel):
    contestant = models.ForeignKey(Contestant)
    event = models.ForeignKey(Event)
    is_approved = models.BooleanField(default=False)

    class Meta(OrderedModel.Meta):
        pass

    def __str__(self):
        return "{edition}: {who} to go to {where}{approved}".format(
            edition=self.event.edition,
            who=self.contestant.user,
            where=self.event.center,
            approved=" (approved)" if self.is_approved else "",
        )