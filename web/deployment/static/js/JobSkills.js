$(function(){
    $("#job_role").change(function(){
	  var v = $( "#job_role option:selected" ).text();
	  console.log(v);
      $("#selected_job").text(v);
      $("#selected_job_match").text("Match: 80%");
	  $("#selected_job_need").text("9,000 needed");

   });

});