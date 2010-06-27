from smtplib import SMTP

def send(conf, log, sbj='', body=''):
    smtp_srv, emailsrc, emaildests, title = conf
    if smtp_srv:
        try:
            session = SMTP(smtp_srv)
            session.sendmail(emailsrc, emaildests, "Subject: [%s]: %s\n%s" % (title, sbj, body))
            session.close()
        except Exception,  e:
            log.error("Unable to deliver email: %s", e)
