# -*- coding: utf-8 -*-
"""
    sqs.app
    ~~~~~~~

    Simple Queue Service app.

    :copyright: (c) 2014 by fsp.
    :license: BSD.
"""
from flask import Flask

from .client import Kestrel


app = Flask(__name__)


@app.route('/', methods=["GET"]):
def get():
    return 'GET'


@app.route('/', methods=["POST"]):
def put():
    return 'PUT'


@app.route('/', methods=["DELETE"]):
def delete():
    return 'DELETE'


@app.route('/m', methods=["GET"]):
def m_get():
    return 'mGET'


@app.route('/m', methods=["POST"]):
def m_put():
    return 'mPUT'


if __name__ == "__main__":
    app.run()
