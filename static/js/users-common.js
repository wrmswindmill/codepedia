//刷新验证码
function refresh_captcha(event){
    $.get("/captcha/refresh/?"+Math.random(), function(result){
        $('#'+event.data.form_id+' .captcha').attr("src",result.image_url);
        $('#'+event.data.form_id+' .form-control-captcha[type="hidden"]').attr("value",result.key);
    });
    return false;
}


//注册刷新验证码点击事件
$('#email_register_form .captcha-refresh').click({'form_id':'email_register_form'},refresh_captcha);
$('#email_register_form .captcha').click({'form_id':'email_register_form'},refresh_captcha);
$('#mobile_register_form .captcha').click({'form_id':'jsRefreshCode'},refresh_captcha);
$('#changeCode').click({'form_id':'jsRefreshCode'},refresh_captcha);
$('#jsFindPwdForm .captcha-refresh').click({'form_id':'jsFindPwdForm'},refresh_captcha);
$('#jsFindPwdForm .captcha').click({'form_id':'jsFindPwdForm'},refresh_captcha);
$('#jsChangePhoneForm .captcha').click({'form_id':'jsChangePhoneForm'},refresh_captcha);