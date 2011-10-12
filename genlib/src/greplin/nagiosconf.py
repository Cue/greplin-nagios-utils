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

"""Configuration generator for Nagios."""

import sys



HOST_TMPL = """
define host {
  use        %(use)s
  host_name  %(name)s
  hostgroups %(hostgroups_str)s
  alias      %(alias)s
  address    %(address)s
}
"""



class NagObj(object):
  """base nagios object
  """


  def __init__(self, name):
    object.__init__(self)
    self.name = name



class NagBag(object):
  """bags of nagios objects - take care of creation, name uniqueness, ...
  """


  def __init__(self, typename, klass):
    object.__init__(self)
    self.typename = typename
    self.klass = klass
    self.bag = {}


  def create(self, name):
    """Create a new object with the given name
    """
    assert not name in self.bag

    inst = self.klass(name)
    self.bag[name] = inst
    return inst


  def get(self, name):
    """Get a object by name
    """
    return self.bag.get(name, None)


  def getOrCreate(self, name):
    """Create or get a new object with the given name
    """
    assert name is not None
    name = name.strip()
    assert len(name) > 0

    if name in self.bag:
      return self.bag[name]

    return self.create(name)


  def generate(self, out):
    """Write config fragemts for this bag to the given output stream
    """
    out.write("# %s definitions ----------------\n" % self.typename)
    for item in self.bag.values():
      out.write('%s\n' % repr(item))




class HostGroup(NagObj):
  """Represent a nagios hostgroup
  """


  def __init__(self, name):
    NagObj.__init__(self, name)


  def __repr__(self):
    return "define hostgroup {\n  hostgroup_name %s \n}" % self.name



class HostGroupBag(NagBag):
  """The set of host groups
  """

  def __init__(self):
    NagBag.__init__(self, 'hostgroup', HostGroup)



HOSTGROUPS = HostGroupBag()



class Host(NagObj):
  """Represent a nagios host
  """


  def __init__(self, name):
    NagObj.__init__(self, name)
    self.use = 'generic-host'
    self.alias = None
    self.address = None
    self.hostgroups = set()
    self.hostgroups_str = None


  def addGroup(self, name):
    """Mark this host as a member of the given group, creating the group if needed
    """
    hg = HOSTGROUPS.get_or_create(name)
    self.hostgroups.add(hg)


  def __repr__(self):
    self.hostgroups_str = ','.join([hg.name for hg in self.hostgroups])
    return HOST_TMPL % self.__dict__



class HostBag(NagBag):
  """The set of hosts
  """

  def __init__(self):
    NagBag.__init__(self, 'host', Host)



HOSTS = HostBag()


def generate(out=sys.stdout):
  """Print nagios configuration fragments to the given output stream
  """
  HOSTGROUPS.generate(out)
  HOSTS.generate(out)

