###
# Copyright (c) 2008, Matthew Sherborne
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import time
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.schedule as schedule
from supybot.ircmsgs import kick, ban, unban
import supybot.callbacks as callbacks
import re


class NoSwear(callbacks.Plugin):
    """Add the help for "@plugin help NoSwear" here
    This should describe *how* to use this plugin."""
    regexps = ['swearWordSnarfer']

    #regex = re.compile(r"(\bdivine-interventions\.com\b|\bfuck\b|\bnigga\b|\bnigger\b|\bshit\b|\bdick\b|\bcunt\b|\bvagina\b|\banus\b|\bbum.*\bhole\b|\borfice\b|\bcum\b|\b(\s\b|\b^)idiot\b|\bfagot\b|\bfaggot\b|\bpenis\b|\bwanker\b|\bf\*ck\b|\bsh\*t\b|\bwtf\b|\bw.t.f\b|\bfuck.n|\bass...+\b)")
# Google url safety api key: ABQIAAAA7uwX-cRMNNMcCmxp5dTwohQwxxvGkHNE4kzqkzBt3ItSoTsMqw
    badWords = ['divine-interventions.com', 'f[*u]ck(ing?)?', 'sh[*i]t', 'cunt', 'an[^t]s', 'bum[^A-Z,a-z]*hole', 'orfice', 'fagg?.t', 'wank(a|er)', 'fuck.n', 'arse', '(ass|arse)(wipe|hole)', 'shit', 'fuck', 'cunt', 'tits', 'mierda', 'cuncha', 'carajo', 'puta']
    badLetters = ['fuck', 'nigga[zs]?', 'nigger', 'c[0o]ck.*sucker', 'm[0o]ther.*fucker']

    _fnUser = re.compile(r'^(?:n|i)=')
    _regex = None

    @property
    def regex(self):
        """
        Builds and caches the great regex
        """
        if self._regex is None:
            r = []
            for word in self.badWords:
                r.append(r'((\W|\b)%s(\W|\b))|' % word)
            for ltrs in self.badLetters:
                r.append(r'(%s)|' % ltrs)
            self._regexString = '.*(' + ((''.join(r))[:-1]) + ').*'
            self._regex = re.compile(self._regexString) # Remove the last |
        return self._regex

    def doPrivmsg(self, irc, msg):
        channel, text = msg.args
        text = text.lower()
        if '#' in channel:
            #print self.regex
            #irc.reply('testing %s against %s' % (text, self._regexString))
            if self.regex.match(text):
                try:
                    hostmask = irc.state.nickToHostmask(msg.nick)
                except KeyError:
                    return
                (nick, user, host) = ircutils.splitHostmask(hostmask)
                user = self._fnUser.sub('*', user)
                banmask = ircutils.joinHostmask('*', user, msg.host)
                if ircutils.hostmaskPatternEqual(banmask, irc.prefix):
                    return
                irc.queueMsg(ban(channel, banmask, 'For swearing. 5 minute timeout'))
                irc.queueMsg(kick(channel, msg.nick, 'For swearing'))
                def unBan():
                    if channel in irc.state.channels and \
                       banmask in irc.state.channels[channel].bans:
                        irc.queueMsg(unban(channel, banmask))
                schedule.addEvent(unBan, time.time()+300)
            elif 'fag' in text.split():
                try:
                    hostmask = irc.state.nickToHostmask(msg.nick)
                except KeyError:
                    return
                (nick, user, host) = ircutils.splitHostmask(hostmask)
                irc.reply('No thanks %s I don\'t smoke' % user)
        return msg


Class = NoSwear


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
