#!/usr/bin/env python
# Copyright 2011 The greplin-nagios-utils Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Server that runs Python checks."""

from eventlet import wsgi, tpool
import eventlet
from flask import Flask, request, make_response, jsonify, abort
APP = Flask(__name__)

import imp
import os
import sys
import logging
from optparse import OptionParser
from collections import defaultdict
from cStringIO import StringIO

# Cache mapping check names to checker modules
CHECK_CACHE = {}
# Argparser options
OPTIONS = None
# Stats on how many times each checker has run
STATS = defaultdict(int)


def runChecker(fun, args):
  """Run a checker function with the given args. Return a string."""
  outStream = StringIO()
  try:
    sys.stdout = outStream
    sys.stderr = outStream
    fun(args)
  except SystemExit:
    pass
  finally:
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
  return outStream.getvalue()


def checker(name):
  """Get a checker function. Caches imports. Writes output to outfile."""
  if name not in CHECK_CACHE:
    filename = os.path.join(os.path.dirname(__file__), OPTIONS.checkdir, 'check_%s.py' % name)
    if os.path.exists(filename):
      CHECK_CACHE[name] = imp.load_source('check_%s' % name, filename)
    else:
      raise KeyError('No such file: %s' % filename)

  return lambda args: runChecker(CHECK_CACHE[name].check, args)


@APP.route('/')
def root():
  """Root request handler."""
  return jsonify(STATS)


@APP.route('/update/<name>')
def update(name):
  """Reload a check module."""
  if name in CHECK_CACHE:
    del CHECK_CACHE[name]
    return "Reloaded"
  else:
    abort(404)


@APP.route('/check/<name>')
def check(name):
  """Run a check."""
  try:
    checkFun = checker(name)
  except KeyError:
    abort(404)

  args = request.args.getlist('arg')
  args.insert(0, 'check_%s' % name)

  output = tpool.execute(checkFun, args)
  if not output.strip(): # If thread pool is wack, run in main thread. Also, pylint: disable=E1103
    logging.warn('Thread pool hiccup. Running %s in main thread.', name)
    output = checkFun(args)
  resp = make_response(output)
  STATS[name] += 1

  resp.headers['Content-Type'] = 'text/plain; charset=UTF-8'
  return resp


def main():
  """Run the server."""
  global OPTIONS                        # pylint: disable=W0603
  parser = OptionParser()
  parser.add_option("-d", "--checkdir", dest="checkdir", metavar="DIR",
                    default="/usr/lib/nagios/plugins", help="directory with check scripts")
  parser.add_option("-l", "--log-level", dest="loglevel", metavar="LEVEL",
                    help="logging level", default='info')
  parser.add_option("-p", "--port", dest="port", metavar="PORT",
                    help="port to listen on", default=8111, type="int")
  OPTIONS = parser.parse_args()[0]

  levelname = {'debug': logging.DEBUG, 'info': logging.INFO, 'warn': logging.WARN, 'error': logging.ERROR}
  logging.basicConfig(level=levelname.get(OPTIONS.loglevel.lower(), logging.WARN))

  wsgi.server(eventlet.listen(('', int(OPTIONS.port))), APP)


if __name__ == '__main__':
  main()
