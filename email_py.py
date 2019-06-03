import os
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

#example with the gmail server and port
Server='smtp.gmail.com'
Port=587
#defining username and password
UserName=
UserPassword=


def SendMail(ImgFileName, subj, text, To):
    msg = MIMEMultipart()
    #set here the complete email address
    From = 
    msg['Subject'] = subj
    msg['From'] = From
    msg['To'] = To
    
    #Server=smtplib.SMTP('smtp.gmail.com')
    text = MIMEText(text)
    msg.attach(text)
    if len(ImgFileName) != 0:
        for item in ImgFileName:
            img_data = open(item, 'rb').read()
            image = MIMEImage(img_data, name=os.path.basename(item))
            msg.attach(image)

    s = smtplib.SMTP(Server, Port)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(UserName, UserPassword)
    s.sendmail(From, To, msg.as_string())
    s.quit()