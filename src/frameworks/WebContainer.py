'''
Created on 13/10/2011

@author: rodm
'''
import webapp2
from google.appengine.api import users
from app.wrapper import menu

class StandardPage(webapp2.RequestHandler): 
    def __init__(self, request, response):
        self.initialize(request, response)
        if users.get_current_user():
            uname = users.get_current_user().email()
        else:
            uname = "anonymous"
            
        self.template_values = {"username":uname, "menu":menu()}
        
        
        
    