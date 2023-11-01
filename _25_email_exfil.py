import smtplib
import time
import win32com.client


stmp_server = 'stmp.example.com'
smtp_port = 587
smtp_account = ''
smtp_password = ''

target_accounts = ['']


def plain_email(subject, contents):
    message = f'Subject: {subject} \n From {smtp_account}\n'
    message += f'To: {target_accounts}\n\n{contents.decode()}'
    server = smtplib.SMTP(stmp_server, smtp_port)
    server.starttls()
    server.login(smtp_account, smtp_password)
    # server.set_debuglevel(1)
    server.sendmail(smtp_account, target_accounts, message)
    time.sleep(1)
    server.quit()


def outlook(subject, contents):
    """
    参考：https://learn.microsoft.com/en-us/office/vba/api/outlook.mailitem
    :param subject:
    :param contents:
    :return:
    """
    # 打开进程.Creates a Dispatch based COM object.
    outlook = win32com.client.Dispatch("Outlook.Application")
    # 创建MailItem对象
    message = outlook.CreateItem(0)
    message.DeleteAfterSubmit = True  # 发送邮件后将其立即删除
    message.Subject = subject
    message.Body = contents.decode()
    message.To = target_accounts[0]
    message.Send()


if __name__ == '__main__':
    plain_email('test message', b'attct.')
