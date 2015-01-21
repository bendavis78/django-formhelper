from __future__ import unicode_literals

import re

from django import forms
from django.forms.forms import BoundField
from django import template
from django.template.loader import get_template

register = template.Library()
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def parse_tokens(parser, tokens):
    """
    Shortcut for parsing args/kwargs from a list of tokens
    """
    args = []
    kwargs = []

    for token in tokens:
        if '=' in token:
            key, token = token.split('=')
            kwargs.append((key, parser.compile_filter(token)))
        else:
            args.append(parser.compile_filter(token))

    return args, dict(kwargs)


class FieldContainerNode(template.Node):
    """
    Represents either a {% form_field %} or a {% form_group %}
    """
    def __init__(self, tag_name, *args, **kwargs):
        self.tag_name = tag_name
        self.template = 'formhelper/{0}.html'.format(tag_name)
        self.args = args
        self.kwargs = kwargs

    def get_form(self):
        if not hasattr(self, '_form'):
            form = None
            arg = self.args[0].resolve(self.context)
            if isinstance(arg, forms.Form):
                form = arg
                self.args = self.args[1:]
            if not form:
                form = self.context.get('form')
            if not form:
                raise template.TemplateSyntaxError(
                    "A form instance must be provided as the first argument "
                    "to {{% {0} %}}, or else it must exist in the context as "
                    "'form'.".format(self.tag_name))
            self._form = form

        return self._form

    def get_fields(self, form):
        fields = []
        for arg in self.args:
            field = arg.resolve(self.context)
            if isinstance(field, BoundField):
                field = field.name
            elif isinstance(field, forms.Field):
                raise template.TemplateSyntaxError(
                    "'{0!r}' is not a bound field'".format(field))
            try:
                field = form[field]
            except KeyError:
                raise template.TemplateSyntaxError(
                    "'{0}' is not a field in {1!r}".format(field, form))
            fields.append(field)
        return fields

    def render(self, context):
        self.context = context
        with context.push():
            tpl = get_template(self.template)
            form = self.get_form()
            fields = self.get_fields(form)
            for k, v in self.kwargs.items():
                context[k] = v.resolve(context)
            context['form'] = form
            context['fields'] = fields
            context['field'] = fields[0]
            html = tpl.render(context)
        return html


def parse_field_tokens(parser, token):
    tokens = token.split_contents()
    name = tokens[0]
    if not len(tokens) > 1:
        raise template.TemplateSyntaxError(
            "{0} takes at least one argument".format(name))
    args, kwargs = parse_tokens(parser, tokens[1:])
    if not args:
        raise template.TemplateSyntaxError(
            "Missing position argument for field name")
    return name, args, kwargs


@register.tag
def field(parser, token):
    """
    Renders the given field name using "formhelper/field.html". The basic
    syntax is:

        {% field form "field_name"  %}

    If a form object exists in the context as "form", it can be omitted from
    the arguments. For example:

        {% with signup_form as form %}
            {% field "first_name" %}
            {% field "last_name" %}
        {% endwith %}

    Keyword arguments will be passed directly to the template context:

        {% field "categories" extra_help="(check all that apply)" %}

    """
    name, args, kwargs = parse_field_tokens(parser, token)
    if len(args) > 2:
        raise template.TemplateSyntaxError(
            "{% field %} takes no more than two positional arguments")
    return FieldContainerNode(name, *args, **kwargs)


@register.tag
def form_group(parser, token):
    """
    {% form_group %} works the same as {% field %}, but takes multiple fields
    as positional arguments. The group renders using a different template,
    "formhelper/form_group.html", which in turn calls {% field %} to render
    the individual fields. Example:

        {% form_group "city" "state" "zip" %}

    """
    name, args, kwargs = parse_field_tokens(parser, token)
    return FieldContainerNode(name, *args, **kwargs)


@register.filter
def class_names(field):
    """
    Returns a set of class names common to a field, such as "required" for
    required fields, and "error" for fields with an error.
    """
    class_names = [field.name.replace('_', '-')]
    widget_class = pyclass_to_cssclass(field.field.widget.__class__.__name__)
    class_names.append(widget_class)
    if field.field.required:
        class_names.append('required')
    if field.errors:
        class_names.append('error')
    return ' '.join(class_names)


@register.inclusion_tag('formhelper/error_list.html')
def error_list(form, only='', suppress_is_required=0):
    """
    Renders a flat error list showing only as much information as is needed.
    If a field has multiple errors, only the first error is shown. With no
    arguments both non-field and field errors are shown.

    If supress_empty=True, field errors containing the string "is required" are
    ommitted, and a single error is shown saying "Complete all required fields"

        {% error_list suppress_is_required=True %}

    Pass `only="field"` or `only="non_field" to show only fields of that type.

        {% error_list only="non_field" %}
    """
    field_errors = []
    required_field_errors = []

    if not only == 'field':
        non_field_errors = form.non_field_errors

    if not only == 'non_field':
        for field in form:
            if not field.errors:
                continue
            err = field.errors[0]
            if err == field.field.error_messages['required']:
                required_field_errors.append(field)
                if suppress_is_required:
                    continue
            field_errors.append((field, err))

    return {
        'form': form,
        'only': only,
        'field_errors': field_errors,
        'required_field_errors': required_field_errors,
        'non_field_errors': non_field_errors,
        'suppress_is_required': suppress_is_required
    }


@register.filter
def field_value(field):
    """
    Returns the coerced value of a bound field
    """
    value = field.value()
    if value is None:
        return None
    try:
        return field.field.coerce(value)
    except TypeError:
        return None


@register.filter
def formset_verbose_name(formset):
    """
    Returns the verbose name for the given formset
    """
    if hasattr(formset, 'verbose_name'):
        return formset.verbose_name
    if hasattr(formset, 'model'):
        return formset.model._meta.verbose_name
    return ''


@register.filter
def formset_verbose_name_plural(formset):
    """
    Returns the plural verbose name for the given formset
    """
    if getattr(formset, 'verbose_name_plural'):
        return formset.verbose_name_plural
    if getattr(formset, 'model'):
        return formset.model._meta.verbose_name_plural
    return formset_verbose_name(formset) + 's'


@register.filter
def is_empty_form(form):
    """
    Returns True if the form is part of a formset and is the "empty form".
    """
    return form.prefix.endswith('__prefix__')


@register.filter
def required_error(field):
    """
    Evaluate to true if the filtered field has a "this field is required"
    error.
    """
    msg = field.field.error_messages['required']
    return any(e for e in field.errors if e == msg)

@register.simple_tag(takes_context=True)
def formset_opts(context, formset):
    """
    Returns a json object for use in a dynamic formset
    """
    import json
    formset_opts = {}
    opts = context.get('formset_opts')
    if opts:
        formset_opts = opts.get(formset.prefix, {})
    return json.dumps(formset_opts)


def pyclass_to_cssclass(name):
    """
    Converts a ExampleClassName toe example-class-name
    """
    s1 = first_cap_re.sub(r'\1-\2', name)
    return all_cap_re.sub(r'\1-\2', s1).lower()


@register.filter
def error_type(field):
    """
    Returns the error message key for the first error in the field
    """
    if field.errors:
        err = field.errors[0]
        messages = field.field.error_messages
        return next(k for k, v in messages.items() if v == err)
    return ''
