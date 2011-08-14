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

    def send_diff(self, sbj='[Firelet] Diff', body=None, diff={}):
        """Send HTML diff email
        :param sbj: Subject
        :type sbj: str.
        """

        self.send_html(sbj=sbj, tpl='email_diff', d=diff)


    def send_html(self, sbj='Firelet', body=None, tpl=None, d=None):
        """Send an HTML email by forking a dedicated thread.
        
        :param sbj: Subject
        :type sbj: str.
        """

        html = template(tpl, d=d)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = sbj
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


    def _send(self, sender, recipients, smtp_server, msg):
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

