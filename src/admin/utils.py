'''
Created on Jul 28, 2011

@author: rod
'''
from datetime import date, datetime
import re

def validateEmail( email ):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)
    
def validateAmount(amount):
    '''
    Must be greater than $1 and be a full number or a decimal with 2 places
    '''
    return re.match("^[1-9][0-9]*(\.[0-9]{2})?$", amount)

def cleanJSField(field):
    return re.match("^[A-Za-z0-9@._\-=() ]*$", field)

def validInputField(field):
    return re.match("^[A-Za-z0-9@._ ]*$", field)

def validInputFields(fields):
    for field in fields:
        if not validInputField(field): 
            raise KnownError(['The only valid characters are [a-z], [A-Z], [0-9], _, @ and .'])
        elif len(field)>40: raise KnownError(['Data length cannot be greater than 40.'])
        
def convertToDate(c_date):
    '''
    expect a date in the format yyyy-mm-dd
    '''
    dt = c_date.split('-')
    return date(int(dt[0]), int(dt[1]), int(dt[2]))

def convertToStartDay(c_date):
    '''
    expect a date in the format yyyy-mm-dd
    '''
    dt = c_date.split('-')
    return datetime(int(dt[0]), int(dt[1]), int(dt[2]), 0, 0, 0)

def convertToEndDay(c_date):
    '''
    expect a date in the format yyyy-mm-dd
    '''
    dt = c_date.split('-')
    return datetime(int(dt[0]), int(dt[1]), int(dt[2]), 23, 59, 59)

def convertFromDate(c_date):
    '''
    return a date in the format yyyy-mm-dd
    '''
    return str(c_date.year)+'-'+str(c_date.month).zfill(2)+'-'+str(c_date.day).zfill(2)

def convertFromDateTime(c_date):
    '''
    return a date in the format yyyy-mm-dd
    '''
    return str(c_date.year)+'-'+str(c_date.month).zfill(2)+'-'+str(c_date.day).zfill(2)+' '+str(c_date.hour).zfill(2)+':'+str(c_date.minute).zfill(2)

def convertFromDateTimeCalendar(c_date):
    '''
    return a date in the format yyyy-mm-ddTHH:MM:00
    '''
    return str(c_date.year)+'-'+str(c_date.month).zfill(2)+'-'+str(c_date.day).zfill(2)+'T'+str(c_date.hour).zfill(2)+':'+str(c_date.minute).zfill(2)+':00'
        
def extractAllMultiValueFromPost(request):
    multivalues={}
    for key, value in request.POST.iteritems():
        #logging.info("Saving key:%s for value:%s" % (key,value))
        if ("[" in key):
            kv = key.split("[")[0]
            if (multivalues.has_key(kv)):
                multivalues[kv].append(value)
            else:
                multivalues[kv]=[value]
    return multivalues

def extractMultiValueFromPost(request, key):
    multivalues=extractAllMultiValueFromPost(request)
    if multivalues.has_key(key):
        return multivalues[key]
    return [] 
    
class KnownError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)