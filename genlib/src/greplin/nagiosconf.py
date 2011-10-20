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



class NagObj(object):
  """base nagios object
  """

  def __init__(self, name):
    object.__init__(self)
    self.name = name
    self.props = {}
    self.meta = {}


  def __repr__(self):
    assert self.typeName != None
    if not self.props:
      return "# skipped define for empty %s %s\n" % (self.typeName, self.name)

    ret = ["define %s {" % self.typeName ]
    mlen = max([ len(k) for k in self.props.keys()]) + 2
    for k, v in self.props.items():
      ret.append("  %s%s%s" % (k, ' ' * (mlen-len(k)), v))
    ret.append("}")
    return "\n".join(ret)



class NagBag(object):
  """bags of nagios objects - take care of creation, name uniqueness, ...
  """


  def __init__(self, klass):
    object.__init__(self)
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
    for item in self.bag.values():
      out.write('%s\n' % repr(item))




class HostGroup(NagObj):
  """Represent a nagios hostgroup
  """
  typeName = 'hostGroup'


  def __init__(self, name):
    NagObj.__init__(self, name)
    self.members = []


  def add(self, member):
    """Add a host to this group
    """
    self.members.append(member)
    

  def __repr__(self):
    self.props['hostgroup_name'] = self.name
    return NagObj.__repr__(self)



class HostGroupBag(NagBag):
  """The set of host groups
  """

  def __init__(self):
    NagBag.__init__(self, HostGroup)



HOSTGROUPS = HostGroupBag()



class Host(NagObj):
  """Represent a nagios host
  """

  typeName = 'host'


  def __init__(self, name):
    NagObj.__init__(self, name)
    self.hostgroups = set()


  def addGroup(self, name):
    """Mark this host as a member of the given group, creating the group if needed
    """
    hg = HOSTGROUPS.getOrCreate(name)
    self.hostgroups.add(hg)
    hg.add(self)


  def __repr__(self):
    self.props['host_name'] = self.name
    self.props['hostgroups'] = ','.join([hg.name for hg in self.hostgroups])
    return NagObj.__repr__(self)



class HostBag(NagBag):
  """The set of hosts
  """

  def __init__(self):
    NagBag.__init__(self, Host)



HOSTS = HostBag()



class Service(NagObj):
  """Represent a nagios service
  """
  typeName = 'service'



class ServiceBag(NagBag):
  """The set of services
  """

  def __init__(self):
    NagBag.__init__(self, Service)


SERVICES = ServiceBag()


def generate(out=sys.stdout):
  """Print nagios configuration fragments to the given output stream
  """
  HOSTGROUPS.generate(out)
  HOSTS.generate(out)
  SERVICES.generate(out)
