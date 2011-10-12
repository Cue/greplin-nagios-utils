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

"""Setup script for Greplin utilities for generating Nagios configuration."""

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

setup(name='greplin-nagios-genlib',
      version='0.1',
      description='Python utilties for creating Nagios configurations.',
      license='Apache',
      author='Greplin, Inc.',
      url='http://www.github.com/Greplin/greplin-nagios-utils/genlib',
      package_dir = {'':'src'},
      packages = [
        'greplin',
      ],
      namespace_packages = [
        'greplin',
      ],
      test_suite = 'nose.collector',
      zip_safe = True
)
