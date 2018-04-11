function submit (type) {
    type = typeof type !== 'undefined' ? type : 'display';
    console.log(type);
    var input = $('<input>')
                    .attr('type', 'hidden')
                    .attr('name', 'action').val(type);
    $('#search_form').append($(input));
    $('#search_form').submit();
}


function update_date(date_field){
    if (date_field == 'undefined')
	    return;
    var row = date_field.closest('tr');
    var raw_rcid = row.children[0].innerHTML;
    var raw_max_date = row.children[2].innerHTML;
    var raw_date = date_field.value;
    console.log(date_field);
    if(raw_max_date != "" && raw_date >= raw_max_date){
	    var css_class = row.className;
	    if(row.className == "")
	    {
	      css_class = "slow-blank";
	    }
	    set_bck_color(row, "failure-ajax");
	    date_field.value = date_field.defaultValue;
	    console.log(date_field.defaultValue);
	    setTimeout(set_bck_color, 500, row, css_class);
	    return;
    }
    var params = { rc_id: raw_rcid, new_date_raw:raw_date, action:'update_date'} 
    console.log(row);
    invoke_ajax('/reports/admin', 'application/json', 'GET', params, row, date_field);  
}

function invoke_ajax(_url, _dataType, _type, params, row, date_field){
    console.log(_type);
    console.log(jQuery.param(params));
    console.log(row.className);
    $.ajax({
	url: _url+ '?' + jQuery.param(params),
	type: _type,
	success: function(data){
			var css_class = row.className;
			if(row.className == "" || row.className == "success-ajax")
			{
			    css_class = "slow-blank";
			}
			set_bck_color(row, "success-ajax");
			setTimeout(set_bck_color, 500,row, css_class);
		},
	error: function(jqXHR, textStatus, error){
			var css_class = row.className;
			if(row.className == "" || row.className =="failure-ajax")
			{
			    css_class = "slow-blank";
			}
			set_bck_color(row, "failure-ajax");
			setTimeout(set_bck_color, 500, row, css_class);
		}
	});
}

function set_bck_color(element, css_class){
	element.className = css_class; 
}

$('#neg').click(function (){
	$('#dhiv').prop('checked', false);
	$('#dhcv').prop('checked', false);
	$('#dhbv').prop('checked', false);
	$('#visit_date').prop('checked', false);
	submit();
});

function neg_check () {
	if ( $('#dhiv').prop('checked') == false &&
			 $('#dhcv').prop('checked') == false &&
			 $('#dhbv').prop('checked') == false &&
			 $('#visit_date').prop('checked') == false )
	{
		$('#neg').prop('checked', true)
	}
	else
	{
		$('#neg').prop('checked', false)
	}
}

$('#dhiv').click(function (){
	neg_check();
	submit();
})

$('#dhcv').click(function (){
	neg_check();
	submit();
})

$('#dhbv').click(function (){
	neg_check();
	submit();
})

$('#visit_date').click(function (){
	neg_check();
	submit();
})

function set_page (page)
{
	$('input[name=page]').val(page.toString());
	submit();
}

$('#csv_export_btn').click(function (){
    submit('export');
})

$('#clear_reference_number').click(function (){
    $('#reference_number').prop('value','');
    submit();
})

