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

# First argument is the check name.
CHECK=$1
shift

# Build the rest of the arguments into the arg string for the URL.
CHECK_ARGS='arg='
if [ "$#" -gt "0" ]
then
  CHECK_ARGS="arg="$1
  shift
  for ARG in "$@"
  do
    CHECK_ARGS=${CHECK_ARGS}"&arg="${ARG}
  done
fi

RESULT=`curl -s http://localhost:8111/check/${CHECK}?${CHECK_ARGS}`
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
