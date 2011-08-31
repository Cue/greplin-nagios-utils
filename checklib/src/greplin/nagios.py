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

"""The Greplin monitoring package."""

import httplib
import json
import socket
import sys
import time


UNKNOWN = 3

CRITICAL = 2

WARNING = 1

OK = 0

STATUS_NAME = ['OK', 'WARN', 'CRIT', 'UNKNOWN']


def wgetWithTimeout(host, port, path, timeout, secure = False):
  """Gets an http page, but times out if it's too slow."""
  start = time.time()
  try:
    if secure:
      conn = httplib.HTTPSConnection(host, port, timeout=timeout)
    else:
      conn = httplib.HTTPConnection(host, port, timeout=timeout)
    conn.request('GET', path)
    body = conn.getresponse().read()
    return time.time() - start, body

  except (socket.gaierror, socket.error):
    print("CRIT: Could not connect to %s" % host)
    exit(CRITICAL)

  except socket.timeout:
    print("CRIT: Timed out after %s seconds" % timeout)
    exit(CRITICAL)


def parseJson(text):
  """Parses JSON, exiting with CRIT if the parse fails."""
  try:
    return json.loads(text)

  except ValueError, e:
    print('CRIT: %s' % e)
    exit(CRITICAL)


def parseJsonFile(filename):
  """Parses JSON from a file, exiting with UNKNOWN if the file does not exist."""
  try:
    with open(filename) as f:
      return parseJson(f.read())
  except IOError, e:
    print('UNKNOWN: %s' % e)
    exit(UNKNOWN)


def lookup(source, *keys, **kw):
  """Successively looks up each key, returning the default keyword arg if a dead end is reached."""
  fallback = kw.get('default')
  try:
    for key in keys:
      source = source[key]
    return source
  except KeyError:
    return fallback
  except AttributeError:
    return fallback
  except TypeError:
    return fallback


def statValue(data, *keys, **kw):
  """Returns the value of a stat."""
  return float(lookup(data, *keys, **kw))


def percent(value):
  """Formats the given float as a percentage."""
  return "%f%%" % (value * 100)


def parseArgs(scriptName, *args, **kw):
  """Parses arguments to the script."""
  argv = kw.get('argv', sys.argv)
  if len(argv) != len(args) + 1:
    print('USAGE: %s %s' % (scriptName, ' '.join([name for name, _ in args])))
    exit(UNKNOWN)

  result = {}
  idx = 0
  for name, fn in args:
    try:
      idx += 1
      result[name] = fn(argv[idx])
    except ValueError:
      print("Invalid value for %s: %r." % (name, argv[1]))
      exit(UNKNOWN)
  return result



class Rule(object):
  """A rule for when to warn or crit based on a stat value."""

  def check(self, value):
    """Checks if this rule should result in a WARN or CRIT."""
    raise NotImplementedError



class Minimum(Rule):
  """A rule that specifies minimum acceptable levels for a metric."""

  def __init__(self, warnLevel, critLevel, unit = ''):
    Rule.__init__(self)
    assert critLevel <= warnLevel
    self.warnLevel = warnLevel
    self.critLevel = critLevel
    self.unit = unit


  def check(self, value):
    """Checks if the given value is under the minimums."""
    if value < self.critLevel:
      return CRITICAL
    elif value < self.warnLevel:
      return WARNING
    else:
      return OK


  def format(self, name, value):
    """Formats as perf data."""
    return "'%s'=%d%s;%d;%d;;;" % (name, value, self.unit, self.warnLevel, self.critLevel)


  def message(self, name, value):
    """Create an error message."""
    if self.check(value) == CRITICAL:
      return '%s: %d%s < %d%s' % (name, value, self.unit, self.critLevel, self.unit)
    elif self.check(value) == WARNING:
      return '%s: %d%s < %d%s' % (name, value, self.unit, self.warnLevel, self.unit)



class Maximum(Rule):
  """A rule that specifies maximum acceptable levels for a metric."""

  def __init__(self, warnLevel, critLevel, unit = ''):
    Rule.__init__(self)
    assert critLevel >= warnLevel
    self.warnLevel = warnLevel
    self.critLevel = critLevel
    self.unit = unit


  def check(self, value):
    """Checks if the given value exceeds the maximums."""
    if value > self.critLevel:
      return CRITICAL
    elif value > self.warnLevel:
      return WARNING
    else:
      return OK


  def format(self, name, value):
    """Formats as perf data."""
    return "'%s'=%d%s;%d;%d;;;" % (name, value, self.unit, self.warnLevel, self.critLevel)


  def message(self, name, value):
    """Create an error message."""
    if self.check(value) == CRITICAL:
      return '%s: %d%s > %d%s' % (name, value, self.unit, self.critLevel, self.unit)
    elif self.check(value) == WARNING:
      return '%s: %d%s > %d%s' % (name, value, self.unit, self.warnLevel, self.unit)




class ResponseBuilder(object):
  """NRPE response builder."""

  def __init__(self):
    self._stats = []
    self._status = OK
    self._critMessages = []
    self._warnMessages = []
    self._unknownMessages = []
    self._messages = []


  def addValue(self, name, value):
    """Adds a value to be tracked."""
    self._stats.append("'%s'=%s;;;;;" % (name, str(value)))
    return self


  def addStatLookup(self, name, data, *keys, **kw):
    """Adds a stat from a sequential key lookup."""
    value = lookup(data, *keys, **kw)
    return self.addValue(name, str(value) + kw.get('suffix', ''))


  def addStatChildren(self, name, data, *keys, **kw):
    """Adds a child for each child of the given dict."""
    values = lookup(data, *keys, **kw)
    if values:
      for childName, value in values.items():
        self.addValue(name % childName, str(value) + kw.get('suffix', ''))
    return self


  def addRule(self, name, rule, value):
    """Adds an alert rule and associated performance data."""
    status = rule.check(value)
    if status:
      self._status = max(self._status, rule.check(value))
      self._messages.append(rule.message(name, value))
    self._stats.append(rule.format(name, value))
    return self


  def warnIf(self, condition, message=None):
    """Warn on a given condition."""
    if condition:
      self.warn(message)
    return self


  def critIf(self, condition, message=None):
    """Mark state as critical on the given condition."""
    if condition:
      self.crit(message)
    return self


  def unknownIf(self, condition, message=None):
    """Mark state as unknown on the given condition."""
    if condition:
      self.unknown(message)
    return self


  def warn(self, message=None):
    """Mark state as warning."""
    self._status = max(self._status, WARNING)
    if message is not None:
      self._warnMessages.append(message)
    return self


  def crit(self, message=None):
    """Mark state as critical."""
    self._status = max(self._status, CRITICAL)
    if message is not None:
      self._critMessages.append(message)
    return self


  def unknown(self, message=None):
    """Mark state as unknown."""
    self._status = max(self._status, UNKNOWN)
    if message is not None:
      self._unknownMessages.append(message)
    return self


  def message(self, message):
    """Set the output message."""
    if message:
      self._messages.append(message)
    return self


  def build(self):
    """Builds the response."""
    return ' '.join(self._stats)


  def finish(self):
    """Builds the response, prints it, and exits."""
    output = STATUS_NAME[self._status]
    messages = self._unknownMessages + self._critMessages + self._warnMessages + self._messages
    if messages:
      output += ': ' + (', '.join(messages))
    if self._stats:
      output += '|' + self.build()

    print(output)
    sys.exit(self._status)
