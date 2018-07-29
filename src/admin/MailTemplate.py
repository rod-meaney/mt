'''
Created on Apr 21, 2011

@author: rod
'''
import logging
from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import users
import admin.df

class MailTemplate(admin.df.DomainFramework):
    '''
    Mail template
    '''
    mail_key = db.StringProperty()
    description = db.StringProperty(multiline=True)
    subject = db.StringProperty()
    body = db.StringProperty(multiline=True)
    from_email = db.StringProperty()
    to_email = db.StringProperty()

    def __init__(self, *args, **kwargs):  
        super(MailTemplate, self).__init__(*args, **kwargs) 
    
    def createFromList(self, the_list):
        self.create(the_list[0], the_list[1], the_list[2], the_list[3], the_list[4], the_list[5])
            
    def create(self, mail_key, description, subject, body, from_email, to_email):
        '''
        Creates a basic keyword and puts into the datastore
        '''
        logging.debug("Creating a %s mail template" % (mail_key))
        self.mail_key = mail_key
        self.description = description
        self.subject=subject
        self.body=body
        self.from_email=from_email
        self.to_email=to_email
        self.createNew()
        
    def getMailTemplateByKey(self, mail_key):
        query = MailTemplate.all()
        query.filter("mail_key = ", mail_key)
        return query.fetch(1)[0]
    
def sendTemplateEmail(to, mail_key, insert_classes, send_from_current, file_name, file_data):
    '''
    to -                the person being sent the email
    mail_key -          lookup into the mail templates
    insert_classes -    a (potentially empty) list of classes to add data into the 
                        subject and body.  Notation is <python attr name>..
    '''
    template = MailTemplate().getMailTemplateByKey(mail_key)
    send_to = to
    if send_from_current:
        send_from = users.get_current_user().email()
    else:
        send_from = template.from_email
    if (send_to==""):
        send_to=template.to_email
    if not mail.is_email_valid(send_to):
        # prompt user to enter a valid address
        raise Exception("Sending to email address is invalid")
    else:
        subject = template.subject
        body = template.body
        for class_in in insert_classes:
            body=renderText(body, class_in)
            subject=renderText(subject, class_in)
        if file_name<>None:
            #attach the file
            mail.send_mail(send_from, send_to, subject, body, attachments=[(file_name, file_data)])
        else:
            mail.send_mail(send_from, send_to, subject, body)
        
def renderText(text, class_to_render):
    for key, value in class_to_render.__dict__.iteritems():
        text=text.replace("<"+key+">", str(value))
    logging.info("Final rendered text:"+text)
    return text