
  function hide_reject_labels(){
    $('.rejected').hide();
  }
  function job_app_ineligible(id){
    $('#e_'+id).show();
    $('#t_'+id).show();
    $('#apply_'+id).hide();
  }
 

  $(document).ready(function(){
    $('.select-state').change(function() {
          var state = $(this).val();
          if(state){
              $.ajax({
                  url: "/ajax-state-city/",
                  type: "POST",
                  data: {
                      state : state
                  },
                  success: function(data) {
                      if(data){
                          $('.select-city').html(data.cities);
                          $( ".select-city" ).prop( "disabled", false );
                      } else{
                          $( ".select-city" ).prop( "disabled", true );
                      }
                  }
              });
          }
      });
    
    hide_reject_labels();
    });
