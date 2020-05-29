from .constants  import *
from . import models

def update_ps_language(language, name):
    if isinstance(language, list):
        for lang in language:
            if lang['attrs']['id'] == ICG_PS_LANG:
                lang['value'] = name
    else:
        language['value'] = name
    return language

def get_ps_language(language):
    if isinstance(language, list):
        for lang in language:
            if lang['attrs']['id'] == ICG_PS_LANG:
                return lang['value']
    return language['value']

def get_values_ps_field(field):
    result = {}
    if isinstance(field['language'], list):
        for lang in field['language']:
            result[lang['language']['attrs']['id']] = lang['value']
    else:
        result[field['language']['attrs']['id']] = field['language']['value']
    return result

def update_ps_dict(p_data, category, field):
    trans_cat_list = models.TranslationCategory.objects.filter(cat=category)
    if isinstance(p_data['language'], list):
        for c in p_data['language']:
            result = models.TranslationCategory.objects.filter(cat=category,
                lang__ps_id=c['attrs']['id'])
            c['value'] = getattr(result[0], field)
    elif p_data['language']['value']:
        p_data['language']['value'] = getattr(trans_cat_list[0], field)

    return p_data

