greplin-nagios-utils
====================

Utilities for writing and running nagios checks.
------------------------------------------------

### Rationale

Monitoring is of critical importance for any system - tool like Nagios have taken much of the pain away.  But we still found it
frustrating to write and modify application checks.

#### [checklib](/Greplin/greplin-nagios-utils/tree/master/checklib)

Writing checks for Nagios involves learning a strange language full of semicolons and rules specified in regexes.  We
wanted to make creating and modifying checks to be as easy as possible so first we wrote [checklib](/Greplin/greplin-nagios-utils/tree/master/checklib).

#### [checkserver](/Greplin/greplin-nagios-utils/tree/master/checkserver)

Next we discovered that when you run checks for 100+ machines with 10+ checks each, you start seeing a lot of system load
used just to start and stop python processes.  To solve this problem we wrote [checkserver](/Greplin/greplin-nagios-utils/tree/master/checkserver).

### Status:

This is a very early stage project.  It works for our needs.  We haven't verified it works beyond that.  Issue reports
and patches are very much appreciated!

### Authors:

[Greplin, Inc.](http://www.greplin.com)