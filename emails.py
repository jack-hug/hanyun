from threading import Thread

from flask import current_app, url_for
from flask_mail import Message


def _send_async_mail(app, message):
    from app import mail
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, html):
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to], html=html)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_new_message_email(email, content):
    message_url = url_for('message', _external=True)
    send_mail(subject='There is new message from hanyunmold website', to=current_app.config['HY_ADMIN_EMAIL'],
              html='<p>You have received a new message from the hanyunmold website:</p>'
                   '<p><strong>Content:</strong> %s</p>'
                   '<p><strong>Email:</strong> <a href="mailto:%s">%s</a></p>'
                   '<p>Click the link below to check:</p>'
                   '<p><a href="%s" style="font-size: 16px;">Link to the Messages.</a></p>'
                   '<p><small style="color: #868e96">Do not reply this email.</small></p>'
                   % (content, email, email, message_url))
