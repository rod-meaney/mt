import logging
import webapp2
from frameworks.WebContainer import StandardPage
from google.appengine.ext.webapp import template
from app.wrapper import url_inject
import json
from app.timesheet.TimeSheet import TimesheetEntry
from app.Person import Person
from admin.utils import KnownError
import csv

class TimeSheetHome(StandardPage):
    @url_inject("web")
    def get(self):
        self.response.out.write(template.render('web/timesheet_home.html', self.template_values))
     
class TimeSheetMobile(StandardPage):
    @url_inject("web")
    def get(self):
        person=Person().getCurrentPerson()
        self.template_values['task_list'] = ['-']+person.timesheet_tasks
        self.response.out.write(template.render('web/timesheet_mob.html', self.template_values))

class CSV_down(webapp2.RequestHandler):
    @url_inject("web")
    def get(self):
        start_date=self.request.get('start')
        end_date=self.request.get('end')
        csv_type=self.request.get('type')
        hyphen=self.request.get('hyphen')
        filename='extport_%s_%s_%s.csv' % (csv_type, start_date, end_date)
        writer = csv.writer(self.response.out)
        timesheet = TimesheetEntry()
        if csv_type=='days':
            rows=timesheet.my_timesheets_csv_by_day(start_date, end_date, hyphen)
        else:
            rows=timesheet.my_timesheets_csv(start_date, end_date)
        for x in rows:
            writer.writerow(x)
        self.response.headers.add_header('mimetype', 'text/csv')
        self.response.headers.add_header('Content-Disposition', 'attachment; filename=%s' % filename )

class DataSaveTimeSheet(webapp2.RequestHandler):
    @url_inject("json")
    def post(self):
        ts = TimesheetEntry()
        entry_date = self.request.POST['date'].strip()
        ts.save_timsheet({'task':self.request.POST['task'].strip(),
                          'date':entry_date,
                          'minutes':self.request.POST['minutes'].strip(),
                          'add':self.request.POST['add'].strip()})
        ts_fresh = TimesheetEntry()
        self.response.out.write(json.dumps({"response":ts_fresh.my_timesheets_json(entry_date, entry_date)}))

class DataUpdateTimeSheet(webapp2.RequestHandler):
    @url_inject("json")
    def post(self):
        ts = TimesheetEntry()
        key = ts.update_timsheet({'task':self.request.POST['task'].strip(),
                                  'date':self.request.POST['date'].strip(),
                                  'minutes':self.request.POST['minutes'].strip(),                                  
                                  'key':self.request.POST['key'].strip()})
        self.response.out.write(json.dumps({"response":"timsesheet entry updated", "id":key}))

class DataDeleteTimeSheets(webapp2.RequestHandler):
    @url_inject("json")
    def post(self):
        '''
        Client should only post valid lsist
        '''
        ts = TimesheetEntry()
        list_to_del = ts.extractMultiVlaueFieldFromPost(self.request, 'delete')
        self.response.out.write(json.dumps({"response":ts.delete_timesheets(list_to_del)}))
        
class DataAllTimeSheets(webapp2.RequestHandler):
    @url_inject("json")
    def post(self):
        ts = TimesheetEntry()
        start=self.request.POST['start'].strip()
        end=self.request.POST['end'].strip()
        self.response.out.write(json.dumps({"response":ts.my_timesheets_json(start, end)}))        

app = webapp2.WSGIApplication([('/app/timesheet/delete', DataDeleteTimeSheets),
                                      ('/app/timesheet/save', DataSaveTimeSheet),                                      
                                      ('/app/timesheet/update', DataUpdateTimeSheet),
                                      ('/app/timesheet/all', DataAllTimeSheets),
                                      ('/app/timesheet/csv.*', CSV_down),
                                      ('/app/timesheet/mob.*', TimeSheetMobile),
                                      ('/app/timesheet/.*', TimeSheetHome),],
                                     debug=True)
