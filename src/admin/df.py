'''
Created on May 30, 2011

@author: rod
'''
from google.appengine.ext import db
from google.appengine.api import users
from admin.utils import KnownError
from datetime import datetime
import logging
class DomainFramework(db.Model):
    
    created = db.DateTimeProperty()
    updated = db.DateTimeProperty()
    
    def blank(self):
        for property in self.properties():
            try:
                self.__setattr__(property, "")
            except:
                logging.error("Need to fix framework for:%s", property)   
            
    def createNew(self):
        self.created = datetime.now()
        self.updated = datetime.now()
        self.put()
            
    def update(self):
        self.updated = datetime.now()
        self.put()   
        
    def updateFieldsFromPost(self, request):
        multivalues={}
        for key, value in request.POST.iteritems():
            #logging.info("Saving key:%s for value:%s" % (key,value))
            if ("[" in key):
                kv = key.split("[")[0]
                if (multivalues.has_key(kv)):
                    multivalues[kv].append(value)
                else:
                    multivalues[kv]=[value]
            else:
                if key!="key":
                    self.__setattr__(key,value)
        for key, value in multivalues.iteritems():
            self.__setattr__(key,value)
            
    def extractMultiVlaueFieldFromPost(self, request, field_name):
        multivalue=[]
        for key, value in request.POST.iteritems():
            if key==field_name+"[]":
                multivalue.append(value)
        return multivalue
    
    def delete_list(self, list_of_items):
        ts = self.get(list_of_items)
        for x in ts:
            if users.get_current_user().user_id()<>x.google_id:
                raise KnownError('One or more of the documents are not yours to delete!')
            x.delete()
            
    def blank_for_null(self, value):
        if value is None:
            return ''
        else:
            return value
            