'''
Created on Jul 24, 2011

@author: rod
'''
from google.appengine.ext import db
from admin.utils import KnownError, convertToDate, convertFromDate
from google.appengine.api import users
from admin import df
from app.Person import Person
from datetime import date, timedelta
import logging

class RankList(df.DomainFramework):
    google_id = db.StringProperty()
    title = db.StringProperty()
    description = db.StringProperty(multiline=True)
    
    def __init__(self, *args, **kwargs):  
        super(RankList, self).__init__(*args, **kwargs)

class RankEntry(df.DomainFramework):
    google_id = db.StringProperty()
    name = db.StringProperty()
    rank_list_id = db.StringProperty()
    
    hours = db.IntegerProperty()
    mins = db.IntegerProperty()
    seconds = db.IntegerProperty()
    time_sec = db.IntegerProperty()
    date = db.DateProperty()
    
    def __init__(self, *args, **kwargs):  
        super(RankEntry, self).__init__(*args, **kwargs)

    def toDict(self):
        return {"ts":{"key":str(self.key()),
                        "task":self.task,
                          "minutes":self.minutes,  
                          "date":convertFromDate(self.date)}}
        
    def toCSV(self):
        return [convertFromDate(self.date),
                self.task,
                self.minutes]
        
    def save_entry(self, items):
        '''
        Only save or deleting
        no updating
        '''
        errors=[]
        self.google_id=users.get_current_user().user_id()
        new_item=items['task'].strip()
        if new_item=='':errors.append('Must enter a value for task')  
        self.task=new_item
        
        try:
            self.minutes=int(items['minutes'])
        except:
            errors.append('Minutes must be an integer')
        
        try:
            self.date = convertToDate(items['date']) 
        except:
            errors.append('Invalid date format - yyyy-mm-dd')
            
        if items['add']=='yes':
            Person().updateTimesheetTask(new_item)
        
        if len(errors)>0: raise KnownError(errors)
        self.createNew()
        return str(self.key())

    def my_timesheets(self, start, end):
        query=self.all()
        query.filter("google_id = ", users.get_current_user().user_id())
        query.filter("date >= ", convertToDate(start))
        query.filter("date <= ", convertToDate(end))
        query.order("-date")
        query.order("-created")
        return query.fetch(1000)
        
    def my_timesheets_json(self, start, end):
        result = {"all_ts":[]}
        tss=self.my_timesheets(start, end)
        for ts in tss:
            result['all_ts'].append(ts.toDict())
        return result
    
    def my_timesheets_csv(self, start, end):
        result = []
        tss=self.my_timesheets(start, end)
        for ts in tss:
            result.append(ts.toCSV())
        return result

    def my_timesheets_csv_by_day(self, start, end):
        matrix={}
        tss=self.my_timesheets(start, end)
        for ts in tss:
            val=ts.task.split('-')[0].strip()
            c_date=convertFromDate(ts.date)
            if val in matrix:
                if c_date in matrix[val]:
                    matrix[val][c_date]=matrix[val][c_date]+ts.minutes
                else:
                    matrix[val][c_date]=ts.minutes
            else:
                matrix[val]={c_date:ts.minutes}
        
        result = []
        start_date=convertToDate(start)
        end_date = convertToDate(end)
        delta = timedelta(days=1)
                
        '''
        Create the header
        '''
        header=['']
        i_date = start_date
        while i_date <= end_date:
            header.append(convertFromDate(i_date))
            i_date += delta
        result.append(header)
        
        '''
        iterate through the tasks and date range
        '''
        for x in matrix:
            line=[x]
            i_date = start_date
            while i_date <= end_date:
                c_date = convertFromDate(i_date)
                if c_date in matrix[x]:
                    line.append(matrix[x][c_date])
                else:
                    line.append(0)
                i_date += delta            
            result.append(line)

        return result
    
    def delete_timesheets(self, timesheet_list):
        self.delete_list(timesheet_list)
        return "Deleted %d timesheet(s)" % len(timesheet_list)