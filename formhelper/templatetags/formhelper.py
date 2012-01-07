from django import template
from django.template.loader import get_template
from django import forms
import re

register = template.Library()
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')

@register.filter
def field_error(field):
    if field.errors:
        err = field.errors[0]
        if err == unicode(field.field.error_messages.get('required')):
            err = '%s is required' % field.label
        else:
            err = '%s: %s' % (field.label, err)
        return err
    return ''

@register.filter
def class_names(field):
    class_names = [field.name.replace('_','-')]
    widget_class = pyclass_to_cssclass(field.field.widget.__class__.__name__)
    class_names.append(widget_class)
    if field.field.required:
        class_names.append('required')
    if field.errors:
        class_names.append('error')
    return ' '.join(class_names)

class FormFieldNode(template.Node):
    def __init__(self, form, field):
        if not form:
            form = 'form'
        self.form = template.Variable(form)
        self.field = field

    def render(self, context):
        try:
            form = self.form.resolve(context)
        except template.VariableDoesNotExist:
            raise template.TemplateSyntaxError('a form must either be passed to form_field as first argument or must exist in context as "form"')
        tpl = get_template('formhelper/includes/field.html')
        field = _get_field(self.field, form, context)
        return tpl.render(template.Context({'form':form, 'field':field}))
        
@register.tag
def form_field(parser, token):
    args = token.split_contents()[1:]
    if not args:
        raise template.TemplateSyntaxError("form_field takes at least one argument")
    if len(args) == 1:
        return FormFieldNode(None, args[0])
    return FormFieldNode(args[0], args[1])

class FormRowNode(template.Node):
    def __init__(self, args):
        self.args = args

    def render(self, context):
        tpl = get_template('formhelper/includes/form_row.html')
        if context.get(self.args[0]) and isinstance(context[self.args[0]], forms.Form):
            form = context[self.args[0]]
            field_list = self.args[1:]
        elif context.get('form'):
            form = context['form']
            field_list = self.args
        else:
            raise template.TemplateSyntaxError('a form must either be passed to form_row as first argument or must exist in context as "form"')
        fields = [_get_field(f, form, context) for f in field_list]
        return tpl.render(template.Context({'form': form, 'fields': fields}))
        
@register.tag
def form_row(parser, token):
    args = token.split_contents()[1:]
    if not args:
        raise template.TemplateSyntaxError("form_row takes at least one argument")
    return FormRowNode(args)

@register.inclusion_tag('formhelper/includes/errorlist.html')
def error_list(form, only=''):
    return {'form':form, 'only':only}

@register.filter
def field_value(field):
    value = field.value()
    if value is None:
        return None
    try:
        return field.field.coerce(value)
    except TypeError:
        return None

@register.filter
def formset_verbose_name(formset):
    if getattr(formset, 'verbose_name'):
        return formset.verbose_name
    if getattr(formset, 'model'):
        return formset.model._meta.verbose_name
    return ''

@register.filter
def formset_verbose_name_plural(formset):
    if getattr(formset, 'verbose_name_plural'):
        return formset.verbose_name_plural
    if getattr(formset, 'model'):
        return formset.model._meta.verbose_name_plural
    return formset_verbose_name(formset) + 's'


@register.filter
def is_empty_form(form):
    """
    Whether or not the form is part of a formset and is the "empty form".
    """
    return form.prefix.endswith('__prefix__')

def _get_field(field, form, context):
    try:
        field = template.Variable(field).resolve(context)
    except template.VariableDoesNotExist:
        pass
    if isinstance(field, basestring):
        field = form[field]
    return field

def pyclass_to_cssclass(name):
    s1 = first_cap_re.sub(r'\1-\2', name)
    return all_cap_re.sub(r'\1-\2', s1).lower()

