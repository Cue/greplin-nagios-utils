greplin-nagios-utils: checklib
==============================

Library that makes writing Nagios checks really easy.
-----------------------------------------------------

### Sample

The sample assumes you're also using [checkserver](../checkserver)

	from greplin.nagios import parseArgs, parseJsonFile, statValue, ResponseBuilder

	def check(argv):
	  """Runs the check."""
	  args = parseArgs('check_sample.py', ('HOST', str), ('TIMEOUT', int), argv=argv)
	  data = parseJson(wgetWithTimeout(args['HOST'], 8081, '/metrics', args['TIMEOUT']))

	  (ResponseBuilder()
	      .addValue('SomeStatToTrack', statValue(data, 'myStat', default = 0))
	      .addRule('OutOfMemoryErrors', Maximum(0, 5), statValue(data, 'com.your.server.Servlet', 'OutOfMemory', 'count', default=0))
	      ).finish()
	
This tracks myStat for performance data, and tracks com.your.server.Servlet.OutOfMemory.count for both performance and status.  If
the latter is > 0, the check will return WARN and if it is > 5 it will return CRIT.

For standalone use (without checkserver) just add

	import sys

	if __name__ == '__main__':
	  check(sys.argv)
