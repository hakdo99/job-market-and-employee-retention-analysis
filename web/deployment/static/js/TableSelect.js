$(function(){
    
    $('#employee-form-submit').click(function(e) {
        // e.preventDefault();
        $('#out').text('');
        $('#employee-record tr').filter(':has(:checkbox:checked)').each(function() {
            // this = tr
            // Sample row
            /**
             * <tr>
             *      <td>Cell value 1</td>
             *      <td>Cell value 2</td>
             * </tr>
             */
            $tr = $(this);
            var rowIndex = null;
            var formData = new FormData();
            $('th', $tr).each(function(index) {
                // first column, #
                $th = $(this)[0];
                if (index == 0){
                    rowIndex = parseInt($th.innerText);
                    formData.set("#", rowIndex);
                }
            });
            // var url = '/select_employee_forecast';
            // $.ajax({
            //     url: url,
            //     type: "POST",
            //     contentType:"application/json; charset=utf-8",
            //     dataType: "json",
            //     data: JSON.stringify({rIndex: rowIndex}),
            // });
            //get row values
            // $('#out').append(this.id);
        });
    });
    
    $('.form-check-input').click(function() {
      $('.form-check-input').not(this).prop('checked', false);
    });
    
});