#!/usr/bin/env python
# Copyright 2012 The greplin-nagios-utils Authors.
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

"""Status

nagios config:
use       regular-service
params    $HOSTNAME$
"""


from greplin.nagios import parseArgs, Maximum, ResponseBuilder
import time


def check(argv):
  """Runs the check."""
  _ = parseArgs('check_slow.py', ('NAME', str), argv=argv)
  time.sleep(5)

  (ResponseBuilder().addRule('harrypotter', Maximum(42, 108), 69)).finish()


if __name__ == '__main__':
  import sys
  check(sys.argv)
