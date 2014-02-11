# -*- coding: utf-8 -*-
"""
    sqs.app
    ~~~~~~~

    Simple Queue Service app.

    :copyright: (c) 2014 by fsp.
    :license: BSD.
"""
from flask import Flask

from . import settings


app = Flask(__name__)
app.config.from_object(settings)


import sqs.views
