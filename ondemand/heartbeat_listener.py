#!/usr/bin/env python

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
# Portions created by the Initial Developer are Copyright (C) 2011
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Geo Mealer <gmealer@mozilla.com>
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
# ***** END LICENSE BLOCK ***** */

"""
This is a script to verify that the heartbeats are travelling across the
appropriate queue.
"""

# System default packages
import datetime
import uuid

# Pulse packages
from mozillapulse import consumers


def got_message(data, message):
    received = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
    sent = data['_meta']['sent']

    print 'Got heartbeat; sent: %(sent)s, received: %(received)s' % {
        'sent': sent, 'received': received}
    message.ack()


def main():
    # unique applabel
    label = 'mozmill.heartbeat-%(id)s' % {'id': uuid.uuid1().hex}
    pulse = consumers.PulseTestConsumer(applabel=label)
    print "Registered with pulse server as %(label)s" % {'label': label}

    # Tell the broker what to listen for and give the callback
    pulse.configure(topic='mozmill.heartbeat', callback=got_message)

    # Block and call the callback function when a message comes in
    print "Listening for heartbeats..."
    pulse.listen()


if __name__ == "__main__":
    main()
