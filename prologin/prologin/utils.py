from django.conf import settings
from django.template import VariableDoesNotExist, Variable
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

import enum
import hashlib
import os
import re
import string
import unicodedata
import uuid


def absolute_site_url(request, absolute_path):
    return "{protocol}://{host}{path}".format(
        protocol="https" if request.is_secure() else "http",
        host=settings.SITE_HOST,
        path=absolute_path,
    )


def get_slug(name):
    name = unicodedata.normalize('NFKD', name.lower())
    name = ''.join(x for x in name if x in string.ascii_letters + string.digits + ' _-')
    name = re.sub(r'[^a-z0-9\-]', '_', name)
    return name


def real_value(var, context):
    """Return the real value based on the context."""
    if var is None:
        return None
    try:
        if not isinstance(var, Variable):
            var = Variable(var)
        real_var = var.resolve(context)
    except VariableDoesNotExist:
        real_var = str(var)
    return escape(real_var)


def upload_path(*base_path):
    """
    Generate upload path for a FileInput.
    `base_path`: folder path of where to put the files
    Typical usage:
        FileField(upload_to=upload_path('media', 'pictures'))
    :param base_path: path of the directory (relative to MEDIA_ROOT) where to store the uploads
    :rtype callable
    """
    parts = ['upload']
    parts.extend(base_path)

    def func(instance, filename):
        path, ext = os.path.splitext(filename)
        rand = hashlib.sha1(uuid.uuid4().bytes).hexdigest()
        name = '%s%s' % (rand, ext)
        return os.path.join(*(parts + [name]))
    return func


class ChoiceEnum(enum.Enum):
    @staticmethod
    def labels(func):
        """
        Constructs a class that overloads label_for() to apply :param func on the label.
        LT stands for Label Transform.
        Typical usage:
            @ChoiceEnum.with_labels(str.title)
            class MyEnum(ChoiceEnum):
                foo = 0
                bar = 1
                # Labels will be Foo and Bar.

        :param func: the callable to apply on raw labels; the result will be passed to
                     ugettext_lazy()
        :rtype class
        """
        assert(callable(func))
        def classbuilder(klass):
            klass.label_for = classmethod(lambda cls, member: _(func(member.name)))
            return klass
        return classbuilder

    @staticmethod
    def sort(key=None, reverse=False):
        """
        Constructs a class that overloads _get_choices() to sort the choices using :param key
        and :param reverse.
        :param key: callable to use for sorting; if None, sorts by label (case insensitive)
        :param reverse: reverse the sort order
        :rtype: class
        """
        if key is None:
            key = lambda pair: pair[1].lower()
        else:
            assert(callable(key))
        def classbuilder(klass):
            orig_get_choices = klass._get_choices
            klass._get_choices = classmethod(lambda cls: sorted(orig_get_choices(), key=key, reverse=reverse))
            return klass
        return classbuilder

    @classmethod
    def label_for(cls, member):
        """
        Return the label for a given enum :param member.
        :param member: one of the members of this enum
        :return: (translated) string
        """
        return _(member.name)

    @classmethod
    def _get_choices(cls):
        """
        Override this method in your ChoiceEnum subclass if you need to implement custom
        behavior, eg. if your members are not of the form "name = db_value".
        :return tuple of (db value, user facing string) pairs
        """
        return tuple((m.value, cls.label_for(m)) for m in cls)

    @classmethod
    def choices(cls, empty_label=None):
        """
        Generate a tuple of pairs suitable for Django's `choices` model field kwarg.
        :param empty_label: if provided, use this label instead of the default `-----`
                            for the empty value
        :rtype tuple of (db value, user facing string) pairs
        """
        choices = cls._get_choices()
        if empty_label:
            choices = ((None, empty_label),) + choices
        return choices
