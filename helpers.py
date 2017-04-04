# -*- coding: UTF-8 -*-
#!/usr/bin/env python

import re

def to_slug(text, delimiter='-', to_lower=True):
    if delimiter == '-':
        text = re.sub('[^\w\s-]', '', text).strip()
        if to_lower:
            text = text.lower()
        text = re.sub('\s+', delimiter, text)
        text = re.sub('\-+', '-', text)
    else:
        text = re.sub('[^\w\s_]', '', text).strip()
        if to_lower:
            text = text.lower()
        text = re.sub('\s+', delimiter, text)
        text = re.sub('_+', '_', text)
    return text

class UserAgent(object):
    def __init__(self):
        pass
