from collections import defaultdict
from django import template
from django.conf import settings
from django.template import Library, Node, TemplateSyntaxError
from django.utils.encoding import smart_str
import re
import urllib
import urllib.parse

register = template.Library()


@register.filter
def percentage_to_max(num, max):
    return int(num / max * 100)


@register.filter
def choiceenum_label(enum_member):
    return enum_member.__class__.label_for(enum_member)


@register.filter
def phone_number(num):
    """
    Formats a French phone number: space separated groups of two digits.
    Starts from the end, such that we do not care if it starts like +336, 06, or 6.
    :param num: the phone number to format
    :rtype sting
    """
    num = [c for c in num.strip()[::-1] if not c.isspace()]
    if len(num) % 2 == 1:
        # so zip() does not truncate to min length
        num.append('')
    return '\u00A0'.join(a + b for a, b in zip(num[-1::-2], num[-2::-2]))


# FIXME: in Dango 1.9, the following two tags can be refactored to simple_tag only

@register.simple_tag
def get_setting(name):
    """
    Example usage:
    Contact us at {% get_setting 'CONTACT_EMAIL' %}
    """
    return getattr(settings, name, None)


@register.assignment_tag
def get_setting_var(name):
    """
    Example usage:
    {% get_setting_var 'CONTACT_EMAIL' as email %}
    Contact use at {{ email }}
    """
    return getattr(settings, name, None)


@register.tag(name='captureas')
def do_captureas(parser, token):
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'captureas' node requires a variable name.")

    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()

    return CaptureasNode(nodelist, args)


class CaptureasNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        return ''


@register.tag
def qurl(parser, token):
    """
    Append, remove or replace query string parameters from an url (preserve order)
 
        {% qurl url [param]* [as <var_name>] %}
 
    param:
            name=value: replace all values of name by one value
            name=None: remove all values of name
            name+=value: append a new value for name
            name-=value: remove the value of name with the value
 
    Example::
 
        {% qurl '/search?page=1&color=blue&color=green' order='name' page=None color+='red' color-='green' %}
        Output: /search?color=blue&order=name&color=red
 
        {% qurl request.get_full_path order='name' %}
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument (url)" % bits[0])

    url = parser.compile_filter(bits[1])

    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    qs = []
    if len(bits):
        kwarg_re = re.compile(r"(\w+)(\-=|\+=|=)(.*)")
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, op, value = match.groups()
            qs.append((name, op, parser.compile_filter(value),))

    return QURLNode(url, qs, asvar)


class QURLNode(Node):
    """Implements the actions of the qurl tag."""

    def __init__(self, url, qs, asvar):
        self.url = url
        self.qs = qs
        self.asvar = asvar
        print(self.url, self.qs, self.asvar)

    def render(self, context):
        urlp = list(urllib.parse.urlparse(self.url.resolve(context)))
        query = defaultdict(list, urllib.parse.parse_qs(urlp[4]))
        for name, op, value in self.qs:
            name = smart_str(name)
            value = value.resolve(context)
            value = smart_str(value) if value is not None else None
            print(name, op, value)
            if op == '+=':
                query[name].append(value)
            elif op == '-=':
                try:
                    query[name].remove(value)
                except ValueError:
                    pass
            elif op == '=':
                if value is None:
                    query.pop(name, None)
                else:
                    query[name].append(value)
            print(query)

        urlp[4] = urllib.parse.urlencode(query, True)
        url = urllib.parse.urlunparse(urlp)

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url
