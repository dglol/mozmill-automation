#! /usr/bin/env python

import copy
import mozmill

# Test case to demonstrate that the API cannot easily be used and some code has
# to be shifted around.
#
# Call it like: ./_test.py /Applications/Firefox.app ../mozmill-tests/aurora/tests/functional/


class TestRunCLI(mozmill.CLI):

    # Copy list of parser options and disable unwanted ones
    parser_options = copy.copy(mozmill.CLI.parser_options)
    parser_options.pop(("-s", "--shell",))
    parser_options.pop(("-b", "--binary",))

    def __init__(self, *args, **kwargs):
        mozmill.CLI.__init__(self, *args, **kwargs)

        print self.args[0]
        self.options.debug = True
        self.options.binary = self.args[0]
        self.options.test = [self.args[1]]


def main():
    try:
        run = TestRunCLI().run()
    except Exception, e:
        print str(e)
    finally:
        pass

if __name__ == "__main__":
    main()

