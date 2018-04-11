function clean_rcid()
{
  var field1 = $("#field1")[0]['value'];
  var field2 = $("#field2")[0]['value'];  
  var div = $('#warning')[0];
  if(field1 == field2)
  {
    if(div != undefined)
        div.remove();
   return true;
  }
  else
  {
      if(div == undefined)
      {
              div = $('<div id="warning" class ="alert alert-warning alert-dismissible fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong> Please enter the same number in both boxes</strong></div>');
      }
          $('#field2').after(div);
      return false;
  }
};
function call_submit()
{
  var clean_rcids = clean_rcid();
  if(clean_rcids == true)
  {
    $('#etform').submit();
  }
};
