import webapp2
from app.wrapper import url_inject
import json
from app.Person import Person
import logging

class DataCurrentUserJSON(webapp2.RequestHandler):
    '''@url_inject("json")'''
    def post(self):
        person = Person().getCurrentPerson()
        self.response.out.write(json.dumps({"response":person.toDict()}))

class DataSaveUserList(webapp2.RequestHandler):
    @url_inject("json")
    def post(self):
        list_name = self.request.POST['list_name'].strip()
        sub_list = self.request.POST['list'].split('\n')
        new_list=[]
        for item in sub_list:
            if item.strip()<>'':new_list.append(item.strip())
        person = Person().getCurrentPerson()
        person.updateTimesheetTasks(new_list)
        self.response.out.write(json.dumps({"response":person.toDict()}))

class DataSaveUserField(webapp2.RequestHandler):
    @url_inject("json")
    def post(self):
        new_field_value = self.request.POST['new_field_value'].strip()
        field_name = self.request.POST['field_name'].strip()
        person = Person().getCurrentPerson()
        person.updateField(field_name, new_field_value)
        self.response.out.write(json.dumps({"response":person.toDict()}))
        
app = webapp2.WSGIApplication(
                                     [('/secure/user', DataCurrentUserJSON),
                                      ('/secure/save_user_list', DataSaveUserList),
                                      ('/secure/save_user_field', DataSaveUserField),
                                      ],
                                     debug=True)
