import logging
import webapp2
from frameworks.WebContainer import StandardPage
from google.appengine.ext.webapp import template
import json
from app.wrapper import url_inject
from admin.MailTemplate import MailTemplate

'''
The app.yaml has made this script only available to administrators
'''

class AllMailTemplates(StandardPage):
    @url_inject("web")
    def get(self, request, response):
        query = MailTemplate.all().order('mail_key')
        self.template_values['data'] = query.fetch(1000)
        self.response.out.write(template.render('web/mail_temp_list.html', 
                                        self.template_values))
        
class EditMailTemplates(StandardPage):
    url_inject("web")
    def get(self, request, response):
        doc_id = self.request.url.split("/mt/")[1]
        logging.debug("Requesting mail template:"+doc_id)
        if doc_id=="new":
            mt = MailTemplate()
            mt.blank()
        else:                
            mt = MailTemplate.get(doc_id)
        self.template_values['data'] = mt
        self.response.out.write(template.render('web/mail_temp_edit.html', 
                                        self.template_values))
            
class SaveMailTemplates(StandardPage):
    @url_inject("json")
    def post(self, request, response):
        doc_id = self.request.get("key")
        if doc_id=="":
            #new keyword
            mt = MailTemplate()
            mt.updateFieldsFromPost(self.request)
            mt.createNew()
            doc_id="%s" % mt.key()
            self.response.out.write(json.dumps(
                    {"response":{"message":"created template", "id":doc_id}}))
        else:
            mt = MailTemplate.get(self.request.get("key"))
            mt.updateFieldsFromPost(self.request)
            mt.update()
            self.response.out.write(json.dumps(
                    {"response":{"message":"updated template", "id":doc_id}}))
                            
app = webapp2.WSGIApplication(
                                     [('/admin/mt', AllMailTemplates),   
                                      ('/admin/mt/save', SaveMailTemplates),
                                      ('/admin/mt/.*', EditMailTemplates),],
                                     debug=True)
