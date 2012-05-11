#!/usr/bin/env python

# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the 'License'); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an 'AS IS' basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is MozMill automation code.
#
# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2010, 2011
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Geo Mealer <gmealer@mozilla.com>
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the 'GPL'), or
# the GNU Lesser General Public License Version 2.1 or later (the 'LGPL'),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK ***** */

"""Launches a listener for the on-demand testing system. The listener will only
respond to requests for the specified cluster. The listener will respond to
requests for either the specified platform or for all platforms."""

# System default packages
from optparse import OptionParser
import subprocess
import sys
from time import sleep
import uuid

# Pulse packages
from mozillapulse import consumers

# Globals shared between main() and dispatch()
debug = False
last_exception = None

cluster = None
platform = None

functional_script = None
update_script = None

# Translates platform value into human-readable string
def get_platform_str(platform):
    if platform:
        return 'platform=%(platform)s' % {'platform': platform}
    else:
        return 'all platforms'


# Execute a test script
def exec_test(*args):
    print '  running: %(args)s' % {'args': ' '.join(args)}
    p = subprocess.Popen(args)
    retcode = p.wait()
    print '  finish, return code: %(code)s' % {'code': retcode}


# Handles the logic for whether to ignore a message based on cluster/platform
# Returns True if it's supposed to be executed, False if ignored.
def screen_request(data, cluster, platform, debug):
    # Based on cluster, are we responding to this request?
    # We are if they're equal
    requested_cluster = data['payload']['cluster']
    if requested_cluster != cluster:
        # Ignore
        if debug:
            print 'Received request for cluster=%(cluster)s' % {
                'cluster': requested_cluster}
            print '  request is not for cluster=%(cluster)s, ignoring.' % {
                'cluster': cluster}
        return False

    # Based on platform, are we responding to this request?
    # We are if no platform is requested (i.e. all platforms) or if they match
    requested_platform = data['payload']['platform']
    if requested_platform and (requested_platform != platform):
        # Ignore
        if debug:
            print 'Received request for %(platform)s' % {
                'platform': get_platform_str(requested_platform)}
            print '  request is not for %(platform)s, ignoring.' % {
                'platform': get_platform_str(platform)}
        return False

    # Platform and cluster both acceptable
    return True


# Handler for update requests
def perform_update(data, cluster, platform, update_script, debug):
    # Screen based on cluster and platform. False means screened out.
    if not screen_request(data, cluster, platform, debug):
        return

    branch = data['payload']['branch']
    channel = data['payload']['channel']

    print ('Processing update test request for cluster=%(cluster)s '
           'on %(platform)s...') % {'cluster': cluster,
                                    'platform': get_platform_str(platform)}
    print '  branch=%(branch)s' % {'branch': branch}
    print '  channel=%(channel)s' % {'channel': channel}
    exec_test('python', update_script, branch, platform, channel)

    print 'Listening for next test request...'


# Handler for functional requests
def perform_functional(data, cluster, platform, functional_script, debug):
    # Screen based on cluster and platform. False means screened out.
    if not screen_request(data, cluster, platform, debug):
        return

    branch = data['payload']['branch']

    print ('Processing functional test request for cluster=%(cluster)s '
           'on %(platform)s...') % {'cluster': cluster,
                                    'platform': get_platform_str(platform)}
    print '  branch=%(branch)s' % {'branch': branch}
    exec_test('python', functional_script, branch, platform)

    print 'Listening for next test request...'


# Main callback, figures out test type and distributes accordingly
def dispatch(data, message):
    global last_exception

    try:
        key = data['_meta']['routing_key']
        if key == 'mozmill.update':
            perform_update(data, cluster, platform, update_script, debug)
        elif key == 'mozmill.functional':
            perform_functional(data, cluster, platform, functional_script,
                               debug)
        elif key == 'mozmill.heartbeat':
            # Ignore
            if debug:
                print 'Received heartbeat, ignoring.'
            return
        else:
            # Ignore
            if debug:
                print 'Received message on unknown key=%(key)s, ignoring.' % {
                    'key': key}
            return
    finally:
        last_exception = None
        message.ack()


def main():
    global debug
    global last_exception

    global cluster
    global platform

    global functional_script
    global update_script

    # args/opts
    usage = "%prog [options] cluster platform"

    parser = OptionParser(usage=usage, description=__doc__)
    parser.add_option('-u', '--update',
                      action='store', type='string', dest='update_script',
                      default='./release_update.py',
                      help='update test script to run [default: %default]')
    parser.add_option('-f', '--functional',
                      action='store', type='string', dest='functional_script',
                      default='./release_bft.py',
                      help='functional test script to run [default: %default]')
    parser.add_option('-d', '--debug',
                      action='store_true', dest='debug', default=False,
                      help=('print out extra debug information on ignored '
                            'messages'))
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error('incorrect number of arguments');

    cluster = args[0]
    platform = args[1]
    functional_script = options.functional_script
    update_script = options.update_script
    debug = options.debug

    # Generate a unique applabel
    label = 'mozmill.listener-%s' % (uuid.uuid1().hex)
    pulse = consumers.PulseTestConsumer(applabel=label)
    print 'Registered with pulse server as %(label)s' % {'label': label}

    print 'Deployed for cluster=%(cluster_str)s' % {'cluster_str': cluster}

    print 'Listening for requests that include platform=%(platform)s' % {
        'platform': platform}

    print 'Will run update tests using script=%(script)s' % {
        'script': update_script}

    print 'Will run functional tests using script=%(script)s' % {
        'script': functional_script}

    if debug:
        print '(in debug mode)'

    # Tell the broker what to listen for and give the callback
    pulse.configure(topic='mozmill.#', callback=dispatch)

    # Block and call the callback function when a message comes in
    print 'Listening for test requests...'

    while True:
        try:
            pulse.listen()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception, e:
            message = '%s: %s' % (e.__class__.__name__, str(e))
            if last_exception is not message:
               last_exception = message
               print message
            sleep(1)

if __name__ == '__main__':
    main()
