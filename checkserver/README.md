greplin-nagios-utils: checkserver
=================================

Simple server that runs checks without Python startup overhead
--------------------------------------------------------------

### Dependencies

* [Eventlet](http://eventlet.net/)

* [Flask](http://flask.pocoo.org/)

### Usage

checkserver loads checks located at

    /usr/lib/nagios/plugins/check_<name>.py

when you visit

    http://localhost:8111/check/<name>

Each check will be run in a thread pool. If you want to include arguments, you can do it
like this:

    http://localhost:8111/check/<name>?arg=hello&arg=world

When the check changes, you can reload the changed code by visiting

    http://localhost:8111/update/<name>

That's it!  We also include check.sh which returns the proper exit code from a check. You
can see stats for how many times each check has been called at

    http://localhost:8111/

Using checkserver is simple, run an instance of the server, and then add nagios checks like:

    define command {
        command_name    check_<name>
        command_line    /usr/lib/nagios/plugins/check.sh <name> args like $HOSTNAME$
    }

    define service {
        use                     your-service-type
        service_description     Your Description Here
        check_command           check_<name>
        hostgroup_name          your-hostgroup
    }
