function display(display_type){
	this.table_id="#tt";
	this.table_header="#tth";
	this.table_body="#ttb";
	this.table_footer="#ttf";
	this.chart_id="#chart";
	this.my_variable='ts_search';
	this.total_time_variable="total_time";		
	this.timesheets=[];
	this.timesheets_total=0
}

var ts_search=new display();
var person={}
var g_is_mobile=false;
var running_total=0;
var edit_row=null;
var current_editing_table=null;
var text_validation_text ="Please only use basic text and numbers - also allowed @._-=()";

function minToHourMin(mins){
	var result="";
	var hour=Math.floor(mins/60);
	var min=(mins % 60);
	if (hour>0){result=hour+"h ";}
	if (min>0){
		if (min<10){result+=('0'+min+'m');}
		else {result+=(min+'m');}
	}
	if (result=="") result="0m";
	return result
}

function paintTimesheets(dis, change_in_data){
	$(dis.table_id).empty();
	edit_row=null;
	dis.timesheets_total = 0;	
	$(dis.timesheets).each( function() {
		$(dis.table_id).append("<tr id='"+this.ts.key+"' ondblclick=\"editRow('"+this.ts.key+"', "+dis.my_variable+");\"></tr>");
		rowHtml(this.ts);
		dis.timesheets_total+=this.ts.minutes;
	});
	$(dis.table_id).append("<tr><td></td><td></td><td align='right'><b>Total</b></td><td id='"+dis.total_time_variable+"'>"
			+minToHourMin(dis.timesheets_total)
			+"</td></tr>");
	if (change_in_data){
		//re-compute and display graph
		if (dis.timesheets_total>0){
			$(dis.chart_id).show();
			generateGoogleCoreChart(dis);
		} else {
			$(dis.chart_id).hide();
		}		
	}
}

function rowHtml(ts, task_update){
	var temp_task_value = ts.task;
	if (!(task_update==null)){
		//This feature shows what a bulk change will effect
		temp_task_value = temp_task_value + " ==> " + task_update; 
	}
	$('#'+ts.key).html(
			"<td width='10%'><input type='checkbox' value='"+ts.key+"'></td>"+
			"<td width='20%'>"+ts.date+"</td>"+
			"<td width='55%'>"+temp_task_value+"</td>"+
			"<td width='15%'>"+minToHourMin(ts.minutes)+"</td>");
}

function getTimesheetRow(id, dis){
	for (var i = 0; i < dis.timesheets.length; i++) {
		if (dis.timesheets[i].ts.key==id){return dis.timesheets[i].ts;}
	}
	return null;
}

function editSelectedRow() {
	if (edit_row!=null){
		alert('You can only edit one task at a time.');
	} else {
		var selected = [];
		jQuery.each($('#tt input:checked'), function() {
			selected.push(this.value);
		});
		if (selected.length==0) {
			alert("No items selected to edit");
		} else if (selected.length>1) {
			alert("You can only edit one task at a time.");
		} else {
			edit_row=new editing_row(selected[0], ts_search);
		}			
	}	
}

function editRow(id, dis){
	if (edit_row!=null){
		alert('You can only edit one task at a time.');
	} else {
		edit_row=new editing_row(id, dis);
		current_editing_table = dis;
	}
}

function editing_row(id, dis){
	this.cur_display=dis;
	this.ts=getTimesheetRow(id, dis);
	this.editRowHtml();
}

editing_row.prototype.editRowHtml = function(){
	$('#'+this.ts.key).html("<td>"+
			"<a href=\"javascript:saveWebPage('/app/timesheet/update', 'timesheet update');\"><img src='/web/images/tick-circle-frame-icon.png' /></a>"+
			"<a href=\"javascript:cancelEdit();\"><img src='/web/images/cross-icon.png' /></a>"+
		"</td>"+
		"<td><input class='std_input' type='text' size='10' name=\"date-edit\" id=\"date-edit\" value=\""+this.ts.date+"\"/></td>"+
		"<td><input class='std_input' type='text' size='35' name=\"task-edit\" id=\"task-edit\" value=\""+this.ts.task+"\"/></td>"+
		"<td><input class='std_input' type='text' size='3' name=\"minutes-edit\" id=\"minutes-edit\" value=\""+this.ts.minutes+"\"/></td>");
}

function cancelEdit(){
	rowHtml(edit_row.ts)
	edit_row=null;
}

function updateRunningTotal() {
	var alertStr="This total is a running total of what has been entered in this session and does not take into account any deletes. Use the search feature for exact results.";
	$('#input_total').html("Input (session total <a href='#' onclick=\"alert('"+
		alertStr+"')\">"+
		minToHourMin(running_total)+"</a>)");
}

function addStandardTask(task){
	if (person.timesheet_tasks.indexOf(task)==-1){
		person.timesheet_tasks.push(task);
		person.timesheet_tasks.sort();
		$( "#task" ).autocomplete( "option", "source", person.timesheet_tasks );
	}
}

function loadTimeSheets(){
	var load={};
	load['start']=$('#start_date').val();
	load['end']=$('#end_date').val();
	$.blockUI({ message: "Loading existing timesheets...." }); 
	$.post('/app/timesheet/all', load, 
			function(data) {
				$.unblockUI();
				if (data.error) {writeError(data.error);} else {
					ts_search.timesheets=data.response.all_ts;
					$('#search_legend').text('Search results loaded @ '+nowTime());
					task_sorted=false;
					paintTimesheets(ts_search, true);
				}
			 },'json');	
}

function updateTask(load, dis){
	var ts = getTimesheetRow(load.key, dis);
	//fix the total
	dis.timesheets_total = dis.timesheets_total + parseInt(load.minutes) - ts.minutes;
	$('#'+dis.total_time_variable+'').html(minToHourMin(dis.timesheets_total))
	//update appropriate task
	ts.task=load.task;
	ts.date=load.date
	ts.minutes=parseInt(load.minutes);
	return true;
}

function showBulkChange(){
	if (!isJSCleanText($('#bulk_change_to').val())) {
		alert(text_validation_text);
	}
	$(ts_search.timesheets).each( function() {
		if (this.ts.task.indexOf($('#bulk_change_from').val())!=-1){
			rowHtml(this.ts, this.ts.task.replace($('#bulk_change_from').val(), $('#bulk_change_to').val()));
		}
	});
	$('#bulk_change_apply').show();
}

function applyBulkChange(){
	if (isJSCleanText($('#bulk_change_to').val())) {
		if (confirm('Are you sure - this cannot be reversed. The changes are shown in the task column.')) {
			var new_task_value='';
			$(ts_search.timesheets).each( function() {
				var preLoad={};
				if (this.ts.task.indexOf($('#bulk_change_from').val())!=-1){
					new_task_value = this.ts.task.replace($('#bulk_change_from').val(), $('#bulk_change_to').val()); 
					preLoad['date']=this.ts.date;
					preLoad['minutes']=this.ts.minutes;
					preLoad['key']=this.ts.key;
					preLoad['task']=new_task_value;
					saveWebPage('/app/timesheet/update', "timesheet bulk update", preLoad);
					this.ts.task = new_task_value;
				}
			});		
		}		
	} else {
		alert(text_validation_text+'\n\nDid you change this since testing!');
	}
	paintTimesheets(ts_search);
	$('#bulk_change_apply').hide();
}


function saveWebPage(url, ucase, preLoad) {
	/*
	 * The standard function to post and save data and handle responses
	 */
	var load={};
	var errors=[];	
	var add_std=false;
	var line_edit="";
	switch (ucase) {
		case "timesheet update":
			if (!isDateStd($('#date-edit').val())) errors.push('Invalid date format - yyyy-mm-dd'); 
			load['date']=$('#date-edit').val();			
			basicTextVal('task-edit', 'Must enter a value for task', errors);
			if (!isJSCleanText($('#task-edit').val())) errors.push(text_validation_text);
			load['task']=$('#task-edit').val();
			if (!is_int($('#minutes-edit').val())) errors.push("Please enter only integers for time");
			load['minutes']=$('#minutes-edit').val();
			load['key']=edit_row.ts.key;
			break;
		case "timesheet entry":
			if (!isDateStd($('#date').val())) errors.push('Invalid date format - yyyy-mm-dd'); 
			load['date']=$('#date').val();
			basicTextVal('task', 'Must enter a value for task', errors);
			if (!isJSCleanText($('#task').val())) errors.push(text_validation_text);
			load['task']=$('#task').val();
			load['minutes']=parseInt(getSelectedBox('min'))+parseInt(getSelectedBox('hour'))*60;
			load['add']='no';
			if (!g_is_mobile){
				if ($('#add_std')[0].checked) {
					add_std=true; load['add']='yes';
				}
			}
			break;
		case "timesheet bulk update":
			load=preLoad;
			break;
	}
	if (errors.length > 0) {
		writeError(errors);
	} else {
		$.blockUI({ message: "Saving...." }); 
		$.post(url, load,  
		function(data) {
			$.unblockUI();
			if (data.error) {writeError(data.error);} else {				
				switch (ucase) {
				case "timesheet update":
					writeActionLog(edit_row.ts.date + " " + 
									edit_row.ts.task + " " + 
									minToHourMin(edit_row.ts.minutes) +' changed to '+
									load['date'] + " " + 
									load['task'] + " " +
									minToHourMin(parseInt(load['minutes'])));					
					updateTask(load, current_editing_table);
					rowHtml(getTimesheetRow(edit_row.ts.key, current_editing_table));
					$(current_editing_table.chart_id).attr('src', generateGoogleCoreChart(current_editing_table));
					edit_row=null;
					break;
				case "timesheet entry":
					$('#hour')[0].selectedIndex=0;
					$('#min')[0].selectedIndex=0;
					$('#task').val('');
					writeActionLog(load['task']+' on '+load['date']+' for '+minToHourMin(load['minutes']));
					if (g_is_mobile) {
						$('#pre_defined')[0].selectedIndex=0;
						$('#pre_defined').focus();
					} else {
						//fix up the standard task and set field focus
						if ($('#add_std')[0].checked) addStandardTask(load['task']);
						$('#add_std')[0].checked=false;
						//running_total+=load['minutes'];
						//updateRunningTotal();
						$('#task').focus();
						
						//re-dsiplay the search field
						ts_search.timesheets=data.response.all_ts;
						$('#search_legend').text('Current day results loaded @ '+nowTime());
						$("select#def_search")[0].selectedIndex = 0;
						$('#end_date').val(load['date']);
						$('#start_date').val(load['date']);
						task_sorted=false;
						paintTimesheets(ts_search, true);
					}
					break;
				}				
			}
		 },'json');
	}
}

function changeSearchDates(){
	var days=0;
	$('#end_date').val(dayDeltaToday(0));
	switch ($("#def_search option:selected").val()) {
		case "yesterday":
			days=-1;
			$('#end_date').val(dayDeltaToday(-1));
		break;
		case "today":
		break;
		case "last week":
			days=-7;
		break;
		case "last month":
			days=-31;
		break;			
	}	
	$('#start_date').val(dayDeltaToday(days));
}

function exportCSV(csv_type) {
	var url='/app/timesheet/csv?start='+$('#start_date').val()+'&end='+$('#end_date').val()+'&type='+csv_type;
	if ($('#summarise_hyphen')[0].checked) {
		url+="&hyphen=yes";
	} else {
		url+="&hyphen=no";
	}
	window.open(url);
}

//careful - mixing prototype and jquery....
function group_summary(dis) {
	this.items={};
	this.labels_l=[];
	this.values_l=[];
	this.max=0;
	var task_key;
	for (var i=0; i<dis.timesheets.length; i++){
		task_key=$.trim(dis.timesheets[i].ts.task.split("-")[0]);
		if (task_key in this.items){		
			this.items[task_key]+=dis.timesheets[i].ts.minutes;
		} else {
			this.items[task_key]=dis.timesheets[i].ts.minutes;
		}
	}
	for (var item in this.items) {
		if (this.items[item]>this.max) this.max=this.items[item];
		this.labels_l.push(item+" "+minToHourMin(this.items[item]));
		this.values_l.push(this.items[item]);
	}
}

group_summary.prototype.url_labels = function (){
	return this.labels_l.join('|').replace(' ','+');
}
group_summary.prototype.url_values = function (){
	return this.values_l.join(',');
}
group_summary.prototype.max_value = function (){
	return this.max;
}

function sort_table(dis) {
	/*
	 * This is not scalable and should be using constants
	 * 
	 * == Sort values ==
	 * 0 = not sorted
	 * 1 = sort ascending
	 * 2 = sort descending
	 * 
	 * == column values ==
	 * 1 = date
	 * 2 = task
	 * 3 = time
	 * 
	 */
	this.task_sort=0;
	this.time_sort=0;
	this.date_sort=1; //default
	this.cur_display=dis;
}

sort_table.prototype.sort = function (column){
	if (column==1){
		//date is pre=sorted at backend and uses so (sort order) to do sorting
		if (this.date_sort==2){
			this.cur_display.timesheets.sort(function(a,b){
				return a.ts.so-b.ts.so;
			});
			this.date_sort=1;
		} else {
			this.cur_display.timesheets.sort(function(a,b){
				return b.ts.so-a.ts.so;
			})
			this.date_sort=2;			
		}
		this.task_sort=0;
		this.time_sort=0;	
	} else if (column==2){
		if (this.task_sort==2){
			this.cur_display.timesheets.sort(function(a,b){
				if (a.ts.task.toLowerCase()>b.ts.task.toLowerCase()) return -1;
				if (a.ts.task.toLowerCase()<b.ts.task.toLowerCase()) return 1;
				return 0;
			})
			this.task_sort=1;			
		} else {
			this.cur_display.timesheets.sort(function(a,b){
				if (a.ts.task.toLowerCase()>b.ts.task.toLowerCase()) return 1;
				if (a.ts.task.toLowerCase()<b.ts.task.toLowerCase()) return -1;
				return 0;
			})
			this.task_sort=2;			
		}
		this.date_sort=0;
		this.time_sort=0;
	} else {
		if (this.time_sort==2){
			this.cur_display.timesheets.sort(function(a,b){
				return b.ts.minutes-a.ts.minutes;
			});
			this.time_sort=1;			
		} else {
			this.cur_display.timesheets.sort(function(a,b){
				return a.ts.minutes-b.ts.minutes;
			})
			this.time_sort=2;			
		}		
		this.date_sort=0;
		this.task_sort=0;		
	}
	paintTimesheets(this.cur_display, false);
}

function generateGoogleCoreChart(dis){
	var gs = new group_summary(dis);
	var data_list = [];
	data_list.push(['Task', 'Hours per Day']);
	for (var i = 0; i < gs.labels_l.length; i++) {
		data_list.push([gs.labels_l[i], gs.values_l[i]]);
	}
	var data = google.visualization.arrayToDataTable(data_list);
	var options = {
      title: 'Grouped summary ('+minToHourMin(dis.timesheets_total)+')'
    };
	var chart = new google.visualization.PieChart(document.getElementById('chart'));
    chart.draw(data, options);
}

function generateGraphURL(size, dis){
	//depreciated and replaced with generateGoogleCoreChart 
	var label_size='11';
	var heading_size='16';
	var pic_size='500x200';
	if (size=='large'){
		label_size='14'
		heading_size='24';
		pic_size='750x350';
	}
	var gs = new group_summary(dis);
	return ""+
	"http://chart.apis.google.com/chart"+
    "?chxs=0,000000,"+label_size+
	"&chds=0,"+gs.max_value()+	
	"&chxt=x"+
	"&chs="+pic_size+
	"&cht=p"+
	"&chd=t:"+gs.url_values()+
	"&chl="+gs.url_labels()+
	"&chma=|12"+
	"&chtt=Grouped+summary ("+minToHourMin(dis.timesheets_total)+")"+
	"&chts=676767,"+heading_size;
}

function launchLarge(dis){
	//uses depreciated functionality so no longer used
	var url = generateGraphURL('large', dis);
	window.open(url, 'Grouped summary');
}