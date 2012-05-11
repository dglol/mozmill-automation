# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is MozMill automation code.
#
# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2010
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Henrik Skupin <hskupin@mozilla.com>
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****

import copy
import mozmill
import mozrunner

class MozmillWrapper(mozmill.MozMill):
    """ Wrapper class for the MozMill class. """

    def __init__(self, *args, **kwargs):
        mozmill.MozMill.__init__(self, *args, **kwargs)

        self.report_callback = None

    def get_report(self, *args, **kwargs):
        """ Override method for customized reports. """

        results = mozmill.MozMill.get_report(self, *args, **kwargs)
        if self.report_callback:
            results = self.report_callback(results)

        return results


class MozmillRestartWrapper(mozmill.MozMillRestart, MozmillWrapper):
    """ Wrapper class for the MozMillRestart class. """

    def __init__(self, *args, **kwargs):
        mozmill.MozMillRestart.__init__(self, *args, **kwargs)
        MozmillWrapper.__init__(self, *args, **kwargs)


class MozmillWrapperCLI(mozmill.CLI):
    """ Wrapper class for the Mozmill CLI class.

    The following properties are set directly:
         addons:    List of add-ons to install
         tests:     List of folders/tests to execute
    """

    mozmill_class = MozmillWrapper

    # This is really bad but we have to declare all possible cli options.
    # Otherwise the mozmill.CLI parser is failing.
    # XXX: Can be removed once we do not have to depend on the CLI class anymore
    #      See bug 565733 for the refactoring work.
    parser_options = copy.copy(mozmill.CLI.parser_options)
    parser_options[("--application",)] = dict(dest="application")
    parser_options[("--channel",)] = dict(dest="channel")
    parser_options[("--delay",)] = dict(dest="delay")
    parser_options[("--entities",)] = dict(dest="entities")
    parser_options[("--iterations",)] = dict(dest="iterations")
    parser_options[("--junit",)] = dict(dest="junit_file")
    parser_options[("--no-fallback",)] = dict(dest="no_fallback")
    parser_options[("--no-restart",)] = dict(dest="no_restart")
    parser_options[("--repository",)] = dict(dest="repository")
    parser_options[("--reserved",)] = dict(dest="reserved")
    parser_options[("--screenshot-path",)] = dict(dest="screenshot_path")
    parser_options[("--tag",)] = dict(dest="tags")
    parser_options[("--target-addons",)] = dict(dest="target_addons")
    parser_options[("--target-buildid",)] = dict(dest="target_buildid")
    parser_options[("--with-untrusted",)] = dict(dest="with_untrusted")

    def __init__(self, debug=False, *args, **kwargs):
        mozmill.CLI.__init__(self, *args, **kwargs)

        self.options.debug = debug
        self.report_callback = None


    def _get_binary(self):
        """ Returns the binary to use for testing. """
        return self.options.binary

    def _set_binary(self, value):
        """ Sets the binary to use for testing. """
        self.options.binary = value

    binary = property(_get_binary, _set_binary, None)


    def _get_fails(self):
        """ Returns the failed tests. """
        return self.mozmill.fails

    fails = property(_get_fails, None, None)


    def _get_logfile(self):
        """ Returns the path of the log file. """
        return self.options.logfile

    def _set_logfile(self, value):
        """ Sets the path of the log file. """
        self.options.logfile = value

    logfile = property(_get_logfile, _set_logfile, None)


    def _get_passes(self):
        """ Returns the passed tests. """
        return self.mozmill.passes

    passes = property(_get_passes, None, None)


    def _get_persisted(self):
        """ Returns the persisted object. """
        return self.mozmill.persisted

    def _set_persisted(self, value):
        """ Sets the persisted object. """
        self.mozmill.persisted = value

    persisted = property(_get_persisted, _set_persisted, None)


    def _get_profile(self):
        """ Returns the path of the profile to use. """
        return self.options.profile

    def _set_profile(self, value):
        """ Sets the path of the profile to use. """
        self.options.profile = value

    profile = property(_get_profile, _set_profile, None)


    def _get_report(self):
        """ Returns the URL of the report server. """
        return self.options.report

    def _set_report(self, value):
        """ Sets the URL of the report server. """
        self.options.report = value

    report_url = property(_get_report, _set_report, None)


    def _get_shell(self):
        """ Returns if a Python shell has to be started. """
        return self.options.shell

    def _set_shell(self, value):
        """ Sets if a Python shell has to be started. """
        self.options.shell = value

    shell = property(_get_shell, _set_shell, None)


    def _get_showall(self):
        """ Returns if complete test output is wanted. """
        return self.options.showall

    def _set_showall(self, value):
        """ Sets if complete test output is wanted. """
        self.options.showall = value

    showall = property(_get_showall, _set_showall, None)


    def _get_showerrors(self):
        """ Returns if extended error output is wanted. """
        return self.options.showerrors

    def _set_showerrors(self, value):
        """ Sets if extended error output is wanted. """
        self.options.showerrors = value

    showerrors = property(_get_showerrors, _set_showerrors, None)


    def _get_skipped(self):
        """ Returns the skipped tests. """
        return self.mozmill.skipped

    skipped = property(_get_skipped, None, None)


    def _get_jsbridge_port(self):
        """ Returns the global port value. """
        return self.mozmill.jsbridge_port

    def _set_jsbridge_port(self, value):
        """ Sets if complete test output is wanted. """
        self.mozmill.jsbridge_port = value

    jsbridge_port = property(_get_jsbridge_port, _set_jsbridge_port, None)


    def _get_jsbridge_timeout(self):
        """ Returns the global timeout value. """
        return self.mozmill.jsbridge_timeout

    def _set_jsbridge_timeout(self, value):
        """ Sets if complete test output is wanted. """
        self.mozmill.jsbridge_timeout = value

    jsbridge_timeout = property(_get_jsbridge_timeout, _set_jsbridge_timeout, None)


    def run(self, *args, **kwargs):
        """ Start the test-run. """
        self.mozmill.report_callback = self.report_callback

        try:
            mozmill.CLI.run(self, *args, **kwargs)
        except SystemExit:
            # Mozmill itself calls sys.exit(1) but we do not want to exit
            pass


class MozmillWrapperRestartCLI(mozmill.RestartCLI, MozmillWrapperCLI):
    """ Wrapper class for the Mozmill RestartCLI class. """

    mozmill_class = MozmillRestartWrapper

    parser_options = copy.copy(MozmillWrapperCLI.parser_options)

    def run(self, *args, **kwargs):
        """ Starts the test-run. """
        self.mozmill.report_callback = self.report_callback

        try:
            mozmill.RestartCLI.run(self, *args, **kwargs)
        except SystemExit:
            # Mozmill itself calls sys.exit(1) but we do not want to exit
            pass


class ThunderbirdMozmillWrapperCLI(MozmillWrapperCLI):
    profile_class = mozrunner.ThunderbirdProfile
    runner_class = mozrunner.ThunderbirdRunner

class ThunderbirdMozmillWrapperRestartCLI(MozmillWrapperRestartCLI):
    profile_class = mozrunner.ThunderbirdProfile
    runner_class = mozrunner.ThunderbirdRunner
