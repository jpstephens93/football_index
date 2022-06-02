import email
import smtplib


def send_email(me, p_word, to, subject, body=None):
    """
    Short function to send basic email from one address to another.
    :param p_word: string of sender login password
    :param me: string of sender address
    :param to: string of receiver address
    :param subject: string of email subject
    :param body: string of email body
    :return: generates email
    """
    msg = email.message_from_string(body)
    msg['From'] = me
    msg['To'] = to
    msg['Subject'] = subject

    s = smtplib.SMTP("smtp.live.com", 587)
    s.ehlo()
    s.starttls()
    s.login(me, p_word)

    s.sendmail(me, to, msg.as_string())

    s.quit()
