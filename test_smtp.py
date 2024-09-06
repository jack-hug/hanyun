import smtplib


def test_email_connection(email, password, smtp_server, smtp_port):
    try:
        # 创建SMTP连接
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # 使用TLS加密
        server.login(email, password)  # 登录邮箱

        print(f"成功连接到邮箱: {email}")

        # 关闭连接
        server.quit()
    except smtplib.SMTPAuthenticationError:
        print("登录失败，请检查邮箱地址和密码是否正确。")
    except smtplib.SMTPException as e:
        print(f"连接失败，错误信息: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")


# 示例使用
email = "karen@hanyunmold.com"
password = "!k-#s7U976KaAxB"
smtp_server = "smtphz.qiye.163.com"
smtp_port = 465  # 通常是587或465

test_email_connection(email, password, smtp_server, smtp_port)
