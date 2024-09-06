from flask import url_for, current_app
from threading import Thread
from flask_mail import Message


def _send_async_mail(app, message):
    with app.app_context():
        from app import mail
        mail.send(message)


def send_mail(subject, to, html):
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to], html=html)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_new_message_email():
    send_mail(subject='New Message', to=current_app.config['HY_ADMIN_EMAIL'],
              html='<p>A new message from hanyunmold,click the link below to check:</p>'
                   '<p><a href="%s">Link</a></p>'
                   '<p><small style="color: #868e96">Do not reply this email.</small></p>'
                   % (url_for('message')))
