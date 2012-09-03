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
import logging
from optparse import OptionParser
from collections import defaultdict
from cStringIO import StringIO
from eloise import nagios
from greplin.nagios import GLOBAL_CONFIG

# Cache mapping check names to checker modules
CHECK_CACHE = {}
# Arg parser options
OPTIONS = None
# Stats on how many times each checker has run
STATS = defaultdict(int)
# Graphite reporter
GRAPHITE = None


def runChecker(fun, name, args):
  """Run a checker function with the given args. Return a string."""
  outStream = StringIO()
  GLOBAL_CONFIG.outfile = outStream
  try:
    fun(args)
  except SystemExit:
    pass
  except Exception, e:
    logging.exception('Checker %s failed', name)
    return 'CRIT: Checker exception: %s' % e
  return outStream.getvalue()


def checker(name):
  """Get a checker function. Caches imports. Writes output to outfile."""
  if name not in CHECK_CACHE:
    filename = os.path.join(os.path.dirname(__file__), OPTIONS.checkdir, 'check_%s.py' % name)
    if os.path.exists(filename):
      CHECK_CACHE[name] = imp.load_source('check_%s' % name, filename)
    else:
      raise KeyError('No such file: %s' % filename)

  return lambda args: runChecker(CHECK_CACHE[name].check, name, args)


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
  except KeyError, e:
    print e
    return abort(404)

  args = request.args.getlist('arg')
  args.insert(0, 'check_%s' % name)

  output = tpool.execute(checkFun, args)
  if GRAPHITE:
    try:
      parsed = nagios.parseResponse(output)
    except Exception, e: # ok to catch generic error # pylint: disable=W0703
      print 'During %s: %r' % (name, e)
      parsed = None

    if parsed and parsed[2]:
      for k, v in parsed[2].iteritems():
        if isinstance(v, (int, long, float)):
          parts = ['checkserver', name, k]
          parts.extend(args)
          GRAPHITE.enqueue('.'.join(parts), v)
      if not GRAPHITE.isAlive():
        GRAPHITE.start()

  resp = make_response(output)
  STATS[name] += 1

  resp.headers['Content-Type'] = 'text/plain; charset=UTF-8'
  return resp


def main():
  """Run the server."""
  global OPTIONS # pylint: disable=W0603
  parser = OptionParser()
  parser.add_option("-d", "--checkdir", dest="checkdir", metavar="DIR",
                    default="/usr/lib/nagios/plugins", help="directory with check scripts")
  parser.add_option("-l", "--log-level", dest="loglevel", metavar="LEVEL",
                    help="logging level", default='info')
  parser.add_option("-g", "--graphite", dest="graphite", metavar="GRAPHITE_HOST",
                    help="graphite host, specify as host:post", default='')
  parser.add_option("-p", "--port", dest="port", metavar="PORT",
                    help="port to listen on", default=8111, type="int")
  OPTIONS = parser.parse_args()[0]

  levelName = {'debug': logging.DEBUG, 'info': logging.INFO, 'warn': logging.WARN, 'error': logging.ERROR}
  logging.basicConfig(level=levelName.get(OPTIONS.loglevel.lower(), logging.WARN))

  if OPTIONS.graphite:
    from greplin.scales import util

    host, port = OPTIONS.graphite.split(':')

    global GRAPHITE # pylint: disable=W0603
    GRAPHITE = util.GraphiteReporter(host, int(port))
    GRAPHITE.start()

  wsgi.server(eventlet.listen(('', int(OPTIONS.port))), APP)


if __name__ == '__main__':
  main()
