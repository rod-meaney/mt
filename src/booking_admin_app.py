import webapp2
from frameworks.WebContainer import StandardPage
from google.appengine.ext.webapp import template
from app.wrapper import url_inject
from app.booking.Administrator import Administrator
from app.booking.Booking import Booking
import json
import logging

class BookingAdmin(StandardPage):
    @url_inject("web")
    def get(self):
        admin = Administrator().getAdministrator()
        if admin <> None:
            self.template_values['data'] = admin
        self.response.out.write(template.render('web/booking_admin.html', self.template_values))

class PostAdmin(webapp2.RequestHandler):        
    @url_inject("json")
    def post(self):
        admin = Administrator()
        response = admin.createOrUpdate(self.request)
        self.response.out.write(json.dumps({"response":response}))

class AddSlots(webapp2.RequestHandler):        
    @url_inject("json")
    def post(self):
        booking = Booking()
        response = booking.AddSlots(self.request.POST['slots'].strip())
        self.response.out.write(json.dumps({"response":response}))

class SearchBookings(webapp2.RequestHandler):        
    @url_inject("json")
    def post(self):
        booking = Booking()
        response = booking.allBookingsAdminJson(self.request.POST['start_date'].strip(), self.request.POST['end_date'].strip())
        self.response.out.write(json.dumps({"response":response}))
        
app = webapp2.WSGIApplication([('/app/booking_admin/search_bookings', SearchBookings),
                               ('/app/booking_admin/post_admin', PostAdmin),
                               ('/app/booking_admin/add_slots', AddSlots),
                               ('/app/booking_admin/.*', BookingAdmin),
                               ], debug=True)
