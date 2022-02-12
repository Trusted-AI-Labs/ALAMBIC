import json
from io import BytesIO
import base64

import spacy

from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html_join

register = template.Library()


@register.filter(name='to_name')
def format_attribute_name(key):
    """
    Converts a dictionary key that was passed to the details template context and formats it for display
    """

    display_name = key.replace('_', ' ')  # Underscore to whitespace
    return display_name.upper()


@register.filter(name='get_class')
def get_class(value):
    return value.__class__.__name__


@register.filter(name='wizard_progress')
def get_wizard_progress(current_step, total_steps):
    """
    Gets a current progress value in percent (Used for setting the width of the progress bar)

    :param current_step: The current wizard step
    :type current_step: int
    :param total_steps: The total number of wizard steps
    :type total_steps: int
    :return: The progress in percent
    :rtype: float
    """
    return current_step / total_steps * 100


@register.filter
def render_jsonld(structured_data):
    """
    Renders a list of dicts containing JSON-LD structured data into the proper HTML markup

    :param structured_data: list of dicts containing structured data
    :type structured_data: list(dict)
    :return: HTML string with JSON-LD structured data
    :rtype: str
    """

    # TODO: validation of json-ld data
    ld_str = '<script type="application/ld+json">'

    for sd in structured_data:
        ld_str += json.dumps(sd)

    ld_str += '</script>'

    return mark_safe(ld_str)


@register.filter
def get_dict_item(dictionary, key):
    """
    allows retrieval of a dict item from the value of a variable in templates

    :param dictionary: dict from which to retrieve the value
    :type dictionary: dict
    :param key: value of the variable containing the requested key name
    :type key: str
    :return: value for the given key if present, None otherwise
    :rtype: any or None
    """
    return dictionary.get(key)


@register.inclusion_tag('annotations/image.html')
def convert_image(data):
    image = data.as_image()
    buffer = BytesIO()
    image.save(buffer, "PNG")
    img_str = base64.b64encode(buffer.getvalue())
    return {'img_str': img_str}


@register.simple_tag(name='to_span')
def to_span(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)  # TODO : maybe tokenize in the import step and add to the object ?
    text = enumerate(doc)
    text = format_html_join(
        '', '<span id="{}" class="card-body-span span-{}">{} </span>',
        ((word[0], word[0], word[1]) for word in text)
    )
    return text
