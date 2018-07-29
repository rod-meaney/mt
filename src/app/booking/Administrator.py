'''
Created on Jul 24, 2011

@author: rod
'''
from google.appengine.ext import db
from google.appengine.api import users
from admin import df
from admin.utils import KnownError
import logging

class Administrator(df.DomainFramework):
    google_id = db.StringProperty()
    site_name = db.StringProperty()
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    phone = db.StringProperty()
    booking_email = db.StringProperty()
    mail_subject = db.StringProperty()
    friendly_url = db.StringProperty()
    mail_template = db.StringProperty(multiline=True)
    
    def __init__(self, *args, **kwargs):  
        super(Administrator, self).__init__(*args, **kwargs)

    def createOrUpdate(self, request):
        '''
        Creates admin basic record and puts into the datastore
        '''
        logging.debug("Creating a %s admin record" % (users.get_current_user().user_id()))
        
        query=Administrator.all()
        query.filter("google_id = ", users.get_current_user().user_id())
        result=query.fetch(10)
        if len(result)>1:
            raise KnownError(["User %s has multiple entries..." % users.get_current_user().email()])
        elif len(result)==1:
            result[0].updateFieldsFromPost(request)
            result[0].booking_email=users.get_current_user().email()
            result[0].update()
            return {"saved":"Admin details updated"}
        else:
            admin = Administrator()
            admin.google_id = users.get_current_user().user_id()
            admin.updateFieldsFromPost(request)
            admin.booking_email=users.get_current_user().email()
            admin.createNew()
            return {"saved":"Admin details created"}
    
    def getAdministrator(self):
        query = Administrator.all()
        query.filter("google_id = ", users.get_current_user().user_id())
        result = query.fetch(1)
        if len(result)==1:
            return result[0]
        else:
            return None

    def getAdministratorByUrl(self, url):
        query = Administrator.all()
        query.filter("friendly_url = ", url)
        result = query.fetch(1)
        if len(result)>1:
            raise KnownError(['There are multiple sites with the same url'])
        elif len(result)==1:
            return result[0]
        else:
            raise KnownError(['There is no site for the url you are viewing.  Please check the url.'])        
    
    def toDictSitePublicDetails(self):
        return {"site":{"key":str(self.key()),
                        "site_name":self.site_name}}        
        