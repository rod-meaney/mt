/**
 * @author rod
 */

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

function selectBoxIndex(id, value) {
	var temp = document.getElementById(id);
	for (i = 0; i < temp.options.length; i++){   
		if (value==temp[i].text) return i;
	} 
	return -1;
}

function is_int(value){ 
   for (i = 0 ; i < value.length ; i++) { 
      if ((value.charAt(i) < '0') || (value.charAt(i) > '9')) return false 
    } 
   return true; 
}

function rightStr(str, n){
	var iLen = String(str).length; return String(str).substring(iLen, iLen - n);
}

function nowDateTime(){
	var d = new Date();
	return d.getFullYear()+'-'+rightStr('0'+(d.getMonth()+1),2)+'-'+rightStr('0'+d.getDate(),2)+' '+rightStr('0'+d.getHours(), 2)+':'+rightStr('0'+d.getMinutes(),2)
}

function dateFormat(date_milli1970_str){
	var d = new Date(parseFloat(date_milli1970_str));
	//return d.getFullYear()+'-'+rightStr('0'+(d.getMonth()+1),2)+'-'+rightStr('0'+d.getDate(),2)+' '+rightStr('0'+d.getHours(), 2)+':'+rightStr('0'+d.getMinutes(),2)
	return d.getFullYear()+'-'+rightStr('0'+(d.getMonth()+1),2)+'-'+rightStr('0'+d.getDate(),2)
}

function todayF(){
	return dateFormat((new Date()).getTime());
}

function dayDeltaToday(days){
	return dateFormat((new Date()).getTime() + (1000 * 60 * 60 * 24 * days));
}

function nowTime(){
	var d = new Date();
	return rightStr('0'+(d.getHours()+1),2)+':'+rightStr('0'+(d.getMinutes()+1),2)+':'+rightStr('0'+d.getSeconds(),2);	
}

/**
 * @param	date - date in the format yyyy-mm-dd
 */
function isDateStd(date) {
	var dArr = date.split("-");
	try{if (isDate(dArr[1],dArr[2],dArr[0])) return true;} catch (err) {return false;}
}

function isDate(mm_str,dd_str,yyyy_str) {
   var mm=parseInt(mm_str, 10)-1; var dd = parseInt(dd_str, 10); var yyyy = parseInt(yyyy_str, 10);
   var d = new Date(yyyy,mm,dd);
   return (d.getMonth() == mm) && (d.getDate() == dd) && (d.getFullYear() == yyyy);
}

function setSelectBox(id, value){
	document.getElementById(id).selectedIndex=selectBoxIndex(id, value);
}

function getSelectedBox(id){
	return document.getElementById(id).options[document.getElementById(id).selectedIndex].value;
}

function trim(id){
	$('#'+id).val($.trim($('#'+id).val()));
}

function basicTextVal(id, error, errors){
	trim(id);
	if ($('#'+id).val()=='') errors.push(error);
}

function isValidText(s, l){
	var test_l=40; if (l) test_l=l; 
	if (s.length>test_l) return false;
	var matchme = /^[A-Za-z0-9@._ ]*$/;
	return matchme.test(s);	
}

function isJSCleanText(s){
	var matchme = /^[A-Za-z0-9@._\-=() ]*$/;
	return matchme.test(s);	
}

function isValidEMail (s){   
   var matchme = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,6}))$/;
   return matchme.test(s);
}
function isValidAmount (s){   
   var matchme = /^[1-9][0-9]*(\.[0-9]{2})?$/;
   return matchme.test(s);
}

function writeError(error, mobile) {
	var e_str="== ERROR ==\n\n"
	jQuery.each(error, function() {
		e_str+=this+"\n";
	});
	if (mobile){
		alert(e_str);
		$.mobile.changePage( "#popup", { transition: "pop" , role: "dialog" } );	
	} else {
		//$('#response').html(e_str);
		alert(e_str);
	}
}

function writeActionLog(log){
	$('#recent_actions').append('<tr><td>'+nowTime()+'</td><td>'+log+'</td></tr>')
}

function deleteSelected(table_id, url, success_fn){
	var del = [];
	jQuery.each($('#'+table_id+' input:checked'), function() {
		del.push(this.value);
	});
	if (del.length==0) {
		$('#response').html("No items to delete");
	} else {
		
		$.blockUI({ message: "Deleting...." });
		$.post(url, {'delete':del},  
		function(data) {
			$.unblockUI();
			if (data.error) {writeError(data.error);} else {
				writeActionLog(data.response);
				setTimeout(success_fn, 500);
			}
		 },'json');
	}
}

function fetchPerson(callback){
	$.blockUI({ message: "Fetching personal data...." });
	$.post('/secure/user',
	function(data) {
		$.unblockUI();
		if (data.error) {writeError(data.error);} else {
			person = data.response.person;
			callback();
		}
	 },'json');
}


function loadPersonList(list_name){
	var list_val="";
	jQuery.each(person[list_name], function() {
		list_val+=this+'\n';
	});
	$('#update_list').val(list_val);
}

/**
 * @param list_title	Display on the list box
 * @param list_name		The dictionary item associated with a list 
 * 						on the person object
 * @param list_field_id The field that has the auto-complete on it
 */
function updatePersonList(list_title, list_name, list_field_id){
	loadPersonList(list_name);
	$( "#list-dialog-form" ).dialog({
		height:500,
		width:400,
		modal:true,
		title:'Update ' + list_title,
		buttons: {
			"Save": function() {
				var load={};
				load['list']=$('#update_list').val();
				load['list_name']=list_name;
				$.post('/secure/save_user_list', load, 
						function(data) {
							if (data.error){
								writeError(data.error)
							} else {
								person[list_name]=load['list'].split('\n');
								$( "#"+list_field_id ).autocomplete({source: person[list_name]});
								$( "#"+list_field_id ).focus();
							}
						 },'json');
				$( this ).dialog( "close" );						
			},				
			Cancel: function() {
				$( this ).dialog( "close" );
			}
		}
	});	
}


/**
 * @param field_title	Display title on the list box
 * @param field_name	The dictionary item associated with a list 
 * 						on the person object
 */
function updatePersonField(field_title, field_name){
	$( "#update_field" ).val(person[field_name])
	$( "#field-dialog-form" ).dialog({
		height:150,
		width:200,
		modal:true,
		title:field_title,
		buttons: {
			"Save": function() {
				var load={};
				load['new_field_value']=$('#update_field').val();
				load['field_name']=field_name;
				$.post('/secure/save_user_field', load, 
						function(data) {
							if (data.error){
								writeError(data.error)
							} else {
								person[field_name]=load['new_field_value'];
							}
						 },'json');
				$( this ).dialog( "close" );
			},				
			Cancel: function() {
				$( this ).dialog( "close" );
			}
		}
	});	
}

function formatDateFieldPicker(field_id){
	$( '#'+field_id ).datepicker();
	$( '#'+field_id ).datepicker( "option", "dateFormat", "yy-mm-dd" );
	$( '#'+field_id ).val(todayF());		
}
