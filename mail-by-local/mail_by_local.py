#coding: utf-8
## define encironment
                ##1 邮箱登录信息
                ##2 发件人和收件人信息
                ##3 邮件主题及内容编辑
                ##4 定义收信人以及抄送和暗抄对象
                ##5 添加附件
                ##6 发送邮件

## define encironment
import time
import smtplib
import email.mime.multipart
import email.mime.text
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email(smtp_host, port, sender_address, receiver_address, cc_receiver_address='', subject='', content='', attach_path='', attach_file = ''):
    msg = email.mime.multipart.MIMEMultipart()
    msg['from'] = sender_address
    msg['to'] = receiver_address
    msg['cc'] = cc_receiver_address
    msg['subject'] = subject
    content = content
    txt = email.mime.text.MIMEText(content, 'plain', 'utf-8')
    msg.attach(txt)
    print("准备添加附件...")
    # 添加附件，从本地路径读取。如果添加多个附件，可以定义part_2,part_3等，然后使用part_2.add_header()和msg.attach(part_2)即可。
    if attach_file != '':
        part = MIMEApplication(open(attach_path+attach_file,'rb').read())
        part.add_header('Content-Disposition', 'attachment', filename=attach_file)#给附件重命名,一般和原文件名一样,改错了可能无法打开.
        msg.attach(part)
    mail_to_address = receiver_address.split(";") + cc_receiver_address.split(";")
    smtp = smtplib.SMTP(smtp_host) 
    smtp.sendmail(sender_address, mail_to_address, str(msg))#注意, 这里的收件方可以是多个邮箱,用";"分开, 也可以用其他符号
    print("发送成功！")
    smtp.quit()

if __name__ == "__main__":
    try:
        smtp_host = 'localhost'
        port = 25 
        sender_address ='root'
        receiver_address = 'xxx@xxx.com;xxx1@xxx.com'
        cc_receiver_address = ''
        subject='python test from yangjian'
        content='弱密码-'+str(time.asctime(time.localtime(time.time())))
        attach_path = ""
        attach_file ="201907_MailQureyList.csv"
        send_email(smtp_host, port, sender_address, receiver_address, cc_receiver_address, subject, content, attach_path, attach_file)
    except Exception as err:
        print(err)
