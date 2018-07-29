import webapp2
from frameworks.WebContainer import StandardPage
from google.appengine.ext.webapp import template
from app.wrapper import url_inject
from app.booking.Booking import Booking
import json
from app.booking.Administrator import Administrator

class BookingPage(StandardPage):
    @url_inject("web")
    def get(self):
        try:
            friendly_url = self.request.path.split('app/booking/')[1]
            site = Administrator().getAdministratorByUrl(friendly_url)
            self.template_values['data'] = site
        except:
            self.template_values['data'] = {'site_name':'Please check URL'}
        self.response.out.write(template.render('web/booking.html', self.template_values))

class SearchCalendarBookings(StandardPage):
    @url_inject("json")
    def post(self):
        booking = Booking()
        response = booking.searchBookings(self.request.POST['url'].strip(), 
                        self.request.POST['start'].strip(), 
                        self.request.POST['end'].strip())
        self.response.out.write(json.dumps(response))

app = webapp2.WSGIApplication([('/app/booking/get_bookings', SearchCalendarBookings),
                               ('/app/booking/.*', BookingPage),
                               ],
                                     debug=True)