function saveAdmin(url, ucase) {
	/*
	 * The standard function to post and save data and handle responses
	 */
	load={};
	load["key"]=object_key;
	switch (ucase) {
		case "mt":
			var allInputs = $(":input");
			jQuery.each(allInputs, function() {
				trim(this.name);
				load[this.name]=this.value;
			});
		break;
	}
	$.blockUI({ message: "Saving..." }); 
	$.post(url, load,  
	function(data) {
		$.unblockUI();
		if (data.error) {writeError(data.error);} else {
			document.getElementById('response').innerHTML=data.response.message;
			object_key=data.response.id;
		}
	 },'json');
}