# Firelet - Distributed firewall management.
# Copyright (C) 2010 Federico Ceratto
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from smtplib import SMTP

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from logging import getLogger
log = getLogger(__name__)

from threading import Thread

from bottle import template

class Mailer(object):
    """Email sender
    """
    def __init__(self, sender='firelet@localhost.local',
        recipients='root@localhost.local', smtp_server='localhost'):
        """Initialize email sender
        :param sender: Sender email address
        :type sender: str.
        :param recipients: Recipient email addresses, comma+space separated
        :type recipients: str.
        :param smtp_server: SMTP server
        :type smtp_server: str.
        """
        self._sender = sender
        self._recipients = recipients
        self._smtp_server = smtp_server
        self._threads = []

    def send_msg(self, sbj='Message', body_txt=''):
        """Send generic HTML email
        :param sbj: Subject
        :type sbj: str.
        :param body_txt: Body text
        :type body_txt: str.
        """
        body = {'text': body_txt}
        self.send_html(sbj=sbj, tpl='email_generic', body=body)

    def send_diff(self, diff, sbj='Diff'):
        """Send HTML diff email
        :param sbj: Subject
        :type sbj: str.
        :param diff: Diff
        :type diff: dict.
        """

        self.send_html(sbj=sbj, tpl='email_diff', body=diff)

    def send_html(self, sbj='', body=None, tpl=None):
        """Send an HTML email by forking a dedicated thread.
        :param sbj: Subject
        :type sbj: str.
        :param body: Body contents
        :type body: dict.
        :param tpl: Body template
        :type tpl: str.
        """

        html = template(tpl, body=body)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "[Firelet] %s" % sbj
        msg['From'] = self._sender
        msg['To'] = self._recipients
        part = MIMEText(html, 'html')
        msg.attach(part)

        log.debug("Sending email using %s" % self._smtp_server)
        thread = Thread(None, self._send, '', 
            (self._sender, self._recipients, self._smtp_server, msg.as_string())
        )
        self._threads.append(thread)
        thread.start()


    def _send(self, sender, recipients, smtp_server, msg): # pragma: no cover
        """Deliver an email using SMTP
        """
        try:
            session = SMTP(smtp_server)
            session.sendmail(sender, recipients, msg)
            session.close()
            log.debug('Email sent')
        except Exception, e:
            log.error("Error sending email: %s" % e)

    def join(self):
        """Flush email queue by waiting the completion of the existing threads
        """
        for t in self._threads:
            t.join(5)

