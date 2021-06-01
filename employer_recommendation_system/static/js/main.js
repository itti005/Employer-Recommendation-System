
  function hide_reject_labels(){
    $('.rejected').hide();
  }
  function job_app_ineligible(id){
    console.log("SHOW STATUSS");
    $('#e_'+id).show();
    $('#t_'+id).show();
    $('#apply_'+id).hide();
  }
 
  function check_eligibility(apply_btn,spk_user_id,job_id,rec_user_id){
    console.log(apply_btn,spk_user_id,job_id,rec_user_id)
    apply_btn_id = apply_btn.id;
    $.ajax({
      url: "/check_student_eligibilty",
      data: {
        'job_id' : job_id,
        'spk_user_id' : spk_user_id
      },
      dataType: 'json',
      success:function(data){
        
        var messages = data.is_eligible
        id=apply_btn_id.split('_');
        if (data.is_eligible==true) {
          
          url = $("#student_profile").attr('href');
          window.location.href = url+"/"+job_id
        }else{
          job_app_ineligible(id[1]);
        }
    }});
  }
    $(document).ready(function(){
      alert('here');

      $('#select-state').change(function() {
            var state = $(this).val();
            // alert(state)
            if(state){
                $.ajax({
                    url: "/ajax-state-city/",
                    type: "POST",
                    data: {
                        state : state
                    },
                    success: function(data) {
                        if(data){
                            $('#select-city').html(data.cities);
                            $( "#select-city" ).prop( "disabled", false );
                        } else{
                            $( "#select-city" ).prop( "disabled", true );
                        }
                    }
                });
            }
        });
      
      hide_reject_labels();
      });
