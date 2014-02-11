# -*- coding: utf-8 -*-
"""
    fire
    ~~~~

    Fire the SQS up.

    :copyright: (c) 2014 by fsp.
    :license: BSD.
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from sqs import app


if __name__ == "__main__":
    app.run()
