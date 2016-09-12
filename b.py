#coding:utf-8
from email.mime.text import MIMEText
msg = MIMEText('hello, send by Python...', 'plain', 'utf-8')
import smtplib
server = smtplib.SMTP('smtp.qq.com', 25) # SMTP协议默认端口是25
server.set_debuglevel(1)
server.login('453542772@qq.com', 'nnfrlvioblhcbhab')
server.sendmail('453542772@qq.com', ['453542772@qq.com'], msg.as_string())
server.quit()