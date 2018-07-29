'''
Created on 27 Feb. 2018

@author: roderickmeaney
'''
from google.appengine.ext import db
from google.appengine.api import users
from datetime import datetime, timedelta
from admin import df
from admin.utils import KnownError, convertToDate, convertFromDateTime,\
    convertToStartDay, convertToEndDay, convertFromDate,convertFromDateTimeCalendar
import logging
from app.booking.Administrator import Administrator

class Booking(df.DomainFramework):
    google_id = db.StringProperty()
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    phone = db.StringProperty()
    booking_email = db.StringProperty()
    date_start = db.DateTimeProperty()
    date_end = db.DateTimeProperty()
    status = db.StringProperty()
    comments = db.StringProperty(multiline=True)
    
    def __init__(self, *args, **kwargs):  
        super(Booking, self).__init__(*args, **kwargs)

    def AddSlots(self, booking_list):
        '''
        Creates booking items based on a bulk upload format of
        <yyy-mm-dd> <24hr time start> <24hr time finish>
        '''
        logging.info("Creating booking for %s" % (users.get_current_user().user_id()))
        count = 0
        fail_count = 0
        for line in booking_list.splitlines():
            try:
                date = line.split(' ')[0]
                start = line.split(' ')[1]
                end = line.split(' ')[2]
                booking = Booking()
                booking.google_id = users.get_current_user().user_id()
                booking.date_start = datetime.strptime(date+' '+start, "%Y-%m-%d %H:%M")
                booking.date_end = datetime.strptime(date+' '+end, "%Y-%m-%d %H:%M")
                booking.status = "available"
                booking.first_name=''
                booking.last_name=''
                booking.phone=''
                booking.booking_email = ''
                booking.comments = ''
                booking.createNew()                    
                count += 1
            except:
                fail_count += 1

        if fail_count >0 :
            return {"saved":"%s booking detail(s) created.  There were some errors with %s booking detail(s)." % (count,fail_count) }
        else:
            return {"saved":"%s booking details created" % count}
    
    def getAllBookings(self, start, end, site):
        '''
        Search for bookings between start and end date based on the site
        '''
        query=self.all()
        query.filter("google_id = ", site.google_id)
        query.filter("date_start >= ", convertToStartDay(start))
        query.filter("date_start <= ", convertToEndDay(end))
        query.order("date_start")
        results = query.fetch(1000)
        return results
   
    def allBookingsAdminJson(self, start, end=None):
        '''
        Return bookings in dictionary between start and end date
        If no end date, add 90 days to create end date
        url is passed through
        '''
        result = {"all_bookings":[]}
        if end==None:
            # Add in three months
            start_date = convertToStartDay(start)
            end_date = start_date + timedelta(days=90) #months not valid apparently??
            end = convertFromDate(end_date)
        site = Administrator().getAdministrator()
        result.update(site.toDictSitePublicDetails())                
        bookings=self.getAllBookings(start, end, site)
        count=0
        for booking in bookings:
            count=count+1
            result['all_bookings'].append(booking.toDictAdmin())
            #here - need to add format in dictionary that we want result to come back as
        return result    
 
    def toDictAdmin(self):
        return {"bk":{"key":str(self.key()),
                        "date_start":convertFromDateTime(self.date_start),
                        "date_end":convertFromDateTime(self.date_end),
                        "first_name":self.first_name,
                        "last_name":self.last_name,
                        "phone":self.phone,
                        "booking_email":self.booking_email,
                        "status":self.status,
                        "comments":self.comments}}  

    def searchBookings(self, url, start, end=None):
        '''
        Return bookings in dictionary between start and end date
        If no end date, add 90 days to create end date
        '''
        result = []
        if end==None:
            # Add in three months
            start_date = convertToStartDay(start)
            end_date = start_date + timedelta(days=90) #months not valid apparently??
            end = convertFromDate(end_date)
        site = Administrator().getAdministratorByUrl(url)
        bookings=self.getAllBookings(start, end, site)
        count=0
        for booking in bookings:
            count=count+1
            result.append(booking.toDictSearch())
            #here - need to add format in dictionary that we want result to come back as
        return result

    def toDictSearch(self):
        return {"title":self.status,
                "start":convertFromDateTimeCalendar(self.date_start),
                "end":convertFromDateTimeCalendar(self.date_end),
                "id":str(self.key())}