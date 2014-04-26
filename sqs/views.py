# -*- coding: utf-8 -*-
"""
    sqs.views
    ~~~~~~~~~

    Register actions.

    :copyright: (c) 2014 by fsp.
    :license: BSD.
"""
from flask import request

from sqs import app
from .client import Kestrel


kestrel = Kestrel(app)


@app.route('/', methods=["GET"])
def get():
    msg = kestrel.queue.get('default')
    if msg is not None:
        return msg
    else:
        return 'nothing inside'


@app.route('/', methods=["POST"])
def put():
    msg = str(request.form['message'])
    kestrel.queue.put('default', msg)
    return ''


@app.route('/', methods=["DELETE"])
def delete():
    return 'DELETE'


@app.route('/m', methods=["GET"])
def m_get():
    return 'mGET'


@app.route('/m', methods=["POST"])
def m_put():
    return 'mPUT'


if __name__ == "__main__":
    app.run()
