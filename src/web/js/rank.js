var person={}
var g_is_mobile=false;

function saveWebPage(url, ucase) {
	/*
	 * The standard function to post and save data and handle responses
	 */
	var load={};
	var errors=[];	
	var add_std=false;
	switch (ucase) {
		case "c1":

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
					case "c1":
	
					break;
				}
			}
		 },'json');
	}
}

