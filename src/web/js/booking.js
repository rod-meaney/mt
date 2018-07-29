/**
 * @author rod
 */
var FAILING_TO_CONNECT = "There is currently an issue connecting, please try again later.";
var STANDARD_TEXT_ERROR = "Use numbers, letters, spaces, full stop (.), comma (,), apostrophy (') at (@), colon (:) or underscore (_).  Length < 40 characters";
var EMPTY_TEXT_ERROR = "Cannot be empty.";
var BAD_EMAIL_ERROR = "You have not enetered a valid email address";
var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov'];
var DAYS = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
var resp = null;
//ie lack of indexOf for Array
if(!Array.indexOf){
    Array.prototype.indexOf = function(obj){
        for(var i=0; i<this.length; i++){if(this[i]==obj){return i;}}
        return -1;
    }
}

Array.prototype.removeObj = function(obj){
	var i=this.indexOf(obj);
	if (this.indexOf(obj)>-1){this.splice(i,1);}
}
function rightStr(str, n){
	var iLen = String(str).length; return String(str).substring(iLen, iLen - n);
}
function trim(id){
	$('#'+id).val($.trim($('#'+id).val()));
	return $('#'+id).val(); 
}

function standardProcess(id, errors, load, field_name){
	basicTextVal(id, errors, field_name);
	if (!isValidText(trim(id))) {errors.push(field_name + ' is incorrect.  ' + STANDARD_TEXT_ERROR);} else {load[id]=$('#'+id).val();}
	load[id]=$('#'+id).val();
}

function basicTextVal(id, errors, field_name){
	trim(id);
	if ($('#'+id).val()=='') errors.push(field_name + ' is incorrect.  ' + EMPTY_TEXT_ERROR);
}

function isValidText(s, l){
	var test_l=40; if (l) test_l=l; 
	if (s.length>test_l) return false;
	var matchme = /^[A-Za-z0-9@._ ]*$/;
	return matchme.test(s);	
}

function writeMessage(ucase, message) {
	msg = ucase+'\n\n';
	switch (ucase) {
		case 'Error':
		case 'Saved':
			msg += message;
		break;
		case 'Errors':
			for(var i=0; i<message.length; i++){msg += message[i]+'\n'}
		break;
	}
	alert(msg);
}

function postWeb(ucase) {
	all_urls = {'search bookings':'/app/booking_admin/search_bookings',
				'add slots':'/app/booking_admin/add_slots',
				'get admin':'/app/booking_admin/get_admin',
				'post admin':'/app/booking_admin/post_admin',
				'get bookings':'/app/booking/get_bookings'};
	url = all_urls[ucase];
	/*
	 * The standard function to post and save data and handle responses
	 */
	load={};
	errors=[];
	switch (ucase) {
		case "get bookings":
			//for a particular site
			load['url'] = window.location.pathname.split('/app/booking/')[1];
			load['start_date'] = dateFormat((new Date()).getTime());
		break;
		case "get admin":
						
		break;		
		case "post admin":
			standardProcess('site_name', errors, load, "Site name");
			standardProcess('first_name', errors, load, "First name");
			standardProcess('last_name', errors, load, "Last name");
			standardProcess('phone', errors, load, "Phone");
			standardProcess('mail_subject', errors, load, "eMail subject");
			standardProcess('friendly_url', errors, load, "Friendly URL");
			basicTextVal('mail_template', errors, "eMail template");
			load['mail_template']=$('#mail_template').val();
		break;
		case "add slots":
			basicTextVal('time_slots_entry', errors, "Time slots");
			load['slots']=$('#time_slots_entry').val();
		break;
		case "search bookings":
			//for the logged in user
			//stored as GMT, so convert to GMT range
			load['start_date'] = $('#start_date').val();
			load['end_date'] = $('#end_date').val();
		break;			
	}
	if (errors.length > 0) {
		writeMessage('Errors', errors);
	} else {
		$.blockUI({ message: "Connecting...." });
		$.post(url, load,  
		function(data) {
			if (data.error) {writeMessage('Error', data.error);} else {
			resp = data.response;
			switch (ucase) {
				case "post admin":
					
				break;	
				case "get admin":
					
				break;		
				case "add slots":
					
				break;
				case "get bookings":
					$('#site_name').html(resp.site.site_name);
					paint_bookings(resp.all_bookings);
				break;					
				case "search bookings":
					$("#admin_search").find("tr:gt(0)").remove();
					var d=data.response.all_bookings;
					for (var i=0; i<d.length; i++) {
						$('#admin_search tr:last').after('<tr><td>'+d[i].bk.date_start.split(' ')[0]+'</td>'+
								'<td>'+d[i].bk.date_start.split(' ')[1]+'</td>'+
								'<td>'+d[i].bk.date_end.split(' ')[1]+'</td>'+
								'<td>'+d[i].bk.first_name+'</td>'+
								'<td>'+d[i].bk.last_name+'</td>'+
								'<td>'+d[i].bk.booking_email+'</td>'+
								'<td>'+d[i].bk.phone+'</td>'+
								'<td>'+d[i].bk.status+'</td>'+
								'<td>'+d[i].bk.comments+'</td></tr>');
					}
				break;					
				} //switch	
				//Common responses
				if ('saved' in data.response) {
					writeMessage('Saved', data.response.saved);
				} 
			} //data.error
		},'json').fail(function() { //function data and $.post
			alert(FAILING_TO_CONNECT);
		}).always(function() {      // .fail
			$.unblockUI();
		});;	 					// .always
	}	
}

var booking = null;
function loadBooking(clicked_booking) {
	booking = clicked_booking;
	$('#date').html(booking.start.format("dddd, MMMM Do YYYY"));
	$('#time').html(booking.start.format("h:mm a")+' - '+booking.end.format("h:mm a"));
	swapTo('booking');
}

function saveBooking() {
	//$('#calendar').fullCalendar('removeEvents', [booking._id]);
	booking.title = 'reserved by you just now';
	booking['color'] = 'orange';
	$('#calendar').fullCalendar('updateEvent', booking);
	swapTo("calendar");
}

function swapTo(page){
	admin_pages = ['basic', 'manage'];
	booking_pages = ['calendar','booking'];
	pages = admin_pages;
	if (booking_pages.indexOf(page)>-1) {pages = booking_pages;}
	for (var i=0; i<pages.length; i++){
		$('#'+pages[i]).hide();
		$('#'+pages[i]+'_nav').removeClass("active");
	}
	$('#'+page).show();
	$('#'+page+'_nav').addClass("active");
}
function dateFormat(date_milli1970_str){
	var d = new Date(parseFloat(date_milli1970_str));
	return d.getFullYear()+'-'+rightStr('0'+(d.getMonth()+1),2)+'-'+rightStr('0'+d.getDate(),2)
}
function formatDateFieldPicker(field_id){
	$( '#'+field_id ).datepicker();
	$( '#'+field_id ).datepicker( "option", "dateFormat", "yy-mm-dd" );
	$( '#'+field_id ).val(dateFormat((new Date()).getTime()));	
}
function good_month(date){
	return MONTHS[date.getMonth()] + ' ' + date.getFullYear();
}
function good_day(date){
	return DAYS[date.getDay()] + ' ' + date.getDate();
}
function paint_bookings(){
	
}