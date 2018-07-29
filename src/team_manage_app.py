
import logging
import webapp2
from frameworks.WebContainer import StandardPage
from google.appengine.ext.webapp import template
from app.wrapper import url_inject
from app.Person import Person

class TeamManageHome(StandardPage):
    @url_inject("web")
    def get(self):
        self.response.out.write(template.render('web/team_manage_home.html', self.template_values))

class TeamManageMob(StandardPage):
    @url_inject("web")
    def get(self):
        person=Person().getCurrentPerson()
        self.template_values['task_list'] = ['-']+person.timesheet_tasks
        self.response.out.write(template.render('web/team_manage_mob.html', self.template_values))        

app = webapp2.WSGIApplication([('/app/team-manage/.*', TeamManageHome),],
                                     debug=True)
