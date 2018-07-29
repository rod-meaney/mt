'''
Created on Jul 22, 2011

@author: rod
'''
import logging
from google.appengine.api import users
from google.appengine.ext.webapp import template
import json

def url_inject(url_type):

    def function_wrapper(f):
        def url_wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception, e:
                error(args[0], e)

        def error(url, exception):
            if url_type=="web":
                template_values={}
                if hasattr(exception,"value"):
                    template_values["error"]=exception.value
                else:
                    template_values["error"] = "Unknown exception"
                url.response.out.write(template.render('web/error.html', template_values))
            elif url_type=="json":
                if hasattr(exception,"value"):
                    url.response.out.write(json.dumps({"error":exception.value}))
                else:
                    error="Unknown exception"
                    url.response.out.write(json.dumps({"error":[error]}))
            else:
                logging.info("Do not handle this type!")
                
        return url_wrapper
    return function_wrapper

'''
def simpleMenuItems():
    admin="false"
    name="anonymous"
    if users.is_current_user_admin():admin="true" 
    if not users.get_current_user():name=users.get_current_user().email()
    template_values = {"admin":admin}
    template_values['name']=name
    return template_values
'''

def menu():
    menu_list=[]
    
    #Add all the items to the menu for the web client
    menu_list.append(MenuItem("home", "/")) 
    if not users.get_current_user():
        logging.info("Not authenticated")
    else:
        if users.is_current_user_admin():
            menu_list.append(MenuItem("templates", "/admin/mt"))
        menu_list.append(MenuItem("logout", users.create_logout_url("/")))
        #menu_list.append(MenuItem("email", users.get_current_user().email()))
    
    return menu_list

class MenuItem():
    def __init__(self, name, url):
        self.name=name
        self.url=url