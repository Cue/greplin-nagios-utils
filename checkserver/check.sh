#!/bin/bash

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

RESULT=`curl -s http://localhost:8111/check/$1?arg=$2`
echo $RESULT

IFS='|:'
for x in $RESULT; do
  case $x in
  OK)
    exit 0;;
  WARN)
    exit 1;;
  CRIT)
    exit 2;;
  *)
    exit 3;;
  esac
done