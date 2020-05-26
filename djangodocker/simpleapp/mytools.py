from .constants  import *

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
