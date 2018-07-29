'''
Created on Jul 24, 2011

@author: rod
'''
from google.appengine.ext import db
from google.appengine.api import users
from admin.utils import KnownError
from admin import df
import logging

class Person(df.DomainFramework):
    google_id = db.StringProperty()
    google_email = db.StringProperty()
    name = db.StringProperty()
    timesheet_tasks = db.StringListProperty()
    
    def __init__(self, *args, **kwargs):  
        super(Person, self).__init__(*args, **kwargs)

    def getPersonByGoogleId(self, googleId):
        '''
        Retrieves the person based on their google ID
        If the person does not exist, then returns None
        '''
        query=Person.all()
        query.filter("google_id = ", googleId)
        result=query.fetch(10)
        if len(result)>1:
            raise KnownError(["User %s has multiple entries..." % users.get_current_user().email()])
        elif len(result)==1:
            return result[0]
        else:
            person = Person()
            person.name="";
            person.google_id=users.get_current_user().user_id()
            person.google_email=users.get_current_user().email()
            person.createNew() 
            return person    
        
    def getCurrentPerson(self):
        return self.getPersonByGoogleId(users.get_current_user().user_id())
        
    def getPeopleByGoogleId(self, googleIds):
        query=self.all()
        query.filter("google_id in ", googleIds)
        return query.fetch(1000)  
    
    def toDict(self):
        return {"person":{"name":self.name,
                          "id":self.google_id,  
                          "email":self.google_email,
                          "timesheet_tasks":self.timesheet_tasks}}
        
    def addName(self, new_name):
        '''
        The premise for this code logic is
        1. User cannot change their name
        2. Checks for name in all existing users
        '''
        person = self.getCurrentPerson()
        if person.name <> "": raise KnownError(["Already has a name (%s)" % person.name])
        if new_name=='': raise KnownError(["You must enter the persons name"])
        
        #check for duplicate names
        query=Person.all()
        query.filter("name = ", new_name)
        result=query.fetch(10)
        if len(result)>0:raise KnownError(["Name already exists, please chose another"])        
        
        #do the update
        person.name=new_name
        person.update()        
        
    def updateField(self, field_name, field_value):
        if field_name=='name':
            self.addName(field_value)
        else:
            KnownError(["Attempting to update invalid field (%s)" % field_name])
        
        
    def updateTimesheetTasks(self, tasks):
        person = self.getCurrentPerson()
        person.timesheet_tasks = tasks
        person.timesheet_tasks.sort()
        person.update()

    def updateTimesheetTask(self, task):
        person = self.getCurrentPerson()
        if not (task in person.timesheet_tasks):
            person.timesheet_tasks.append(task)
            person.timesheet_tasks.sort()
            person.update()        