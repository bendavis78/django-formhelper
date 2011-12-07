=================
Django FormHelper
=================

Django FormHelper is a collection of templates and templatetags to ease the 
pain in building out web forms. It does this by breaking the form down into
separate re-usable and customizable components. This allows you to only 
customize the parts you want, and let the rest happen automatically.


Usage
=============
After installing django-formhelper, add ``formhelper`` to your ``INSTALLED_APPS`` in your ``settings.py``.

In your template, you need to load ``formhelper``::

    ...
    {% load formhelper %}
    ...


Template Tags
=============

----------
form_field
----------
Render out a single form field. Uses the template ``formhelper/includes/field.html``.  Example usage::

    {% form_field contact_form first_name %}
 
If your form is in your view's context as the variable "form", you can omit the first argument::

    {% form_field first_name %}

Otherwise, you can use the "with" templatetag::

    {% with my_form as form %}
    ...
    {% form_field first_name %}
    ...
    {% endwith %}


--------
form_row
--------
Like form_field, but renders out multiple fields.  Uses the template ``formhelper/includes/form_row.html``. Example usage::

    {% form_row first_name middle_name last_name %}


----------
error_list
----------
Render out the form error list as an unordered list.  Uses the template ``formhelper/includes/error_list.html``  Example usage::

    {% error_list %}
 
You may also render out only non-field errors or only field-specific errors::

    {% error_list non_field %}
    ... or ...
    {% error_list field %}
 
-----------
class_names
-----------
Renders a list of useful class names for a field that includes the field name, the widget type, whether or not the field is requried, and whether or not the field has an error.

For example, if your field was a textinput named "first_name" and it was required::
    
    <div class="{% field|class_names %}">

would result in::

    <div class="first_name text-input required">

if the field has an error::

    <div class="first_name text-input required error">



Formsets
=========

For easy formset support, complete with javascript (similar to django-admin), simply include the formset template::

    {% include "formhelper/includes/formset.html" %}

This assumes that your formset is in a context variable called "formset".  If not, you can use the "with" tag as described above.


Customizing
===========
You may override any template within your own app's template directory. Just make sure your app comes before the formhelper app in the ``INSTALLED_APPS`` setting. 

The following is a list of templates available:

``formhelper/includes/form.html``

``formhelper/includes/form_row.html``

``formhelper/includes/field.html``

``formhelper/includes/errorlist.html``

``formhelper/includes/errorlist.html``
