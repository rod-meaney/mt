'''
Created on Apr 1, 2012

@author: rod
'''

from google.appengine.ext import db
from admin.utils import KnownError
from google.appengine.api import users
from admin import df
import logging

class Team(df.DomainFramework):
    team_name = db.StringProperty()
    managers = db.ListProperty()
    members = db.ListProperty() #pipe, e-mail, name, optional
    
    
    def __init__(self, *args, **kwargs):  
        super(Team, self).__init__(*args, **kwargs)