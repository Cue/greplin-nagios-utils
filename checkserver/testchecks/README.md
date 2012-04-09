Example checks for testing
---------

These checks are short, don't do much, and are here for testing out the check server. To run them, try this:

    python server.py -d testchecks/

And go to one of the following URLs:

    http://localhost:8111/check/slow?arg=hello
    http://localhost:8111/check/fast?arg=world

The fast check is fast, the slow check takes five seconds.
