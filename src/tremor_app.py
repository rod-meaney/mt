import webapp2
from frameworks.WebContainer import StandardPage
from google.appengine.ext.webapp import template
from app.wrapper import url_inject

class Impairment(StandardPage):
    @url_inject("web")
    def get(self):
        self.response.out.write(template.render('web/tremor.html', self.template_values))

app = webapp2.WSGIApplication([('/app/tremor/.*', Impairment),
                               ],
                                     debug=True)
