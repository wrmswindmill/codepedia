// 点击cancel 关闭输入框
function cancel(){
    var cancelbtn = $('.cancel-button');
      cancelbtn.parent('div').prev('a').show();
      cancelbtn.parent('div').prev('a').prev('div').show();
      cancelbtn.parent('div').hide();

}

// 添加注释按钮的显示隐藏
$(function(){
    var snippetline = $('.snippet-code-line div');
    $.each(snippetline,function(n,element){
      var linenum = n + 1;
      $('#line-'+linenum).hover(function(){
        $('#addannotation_'+linenum).show();
      },function(){
        $('#addannotation_'+linenum).hide();
      })
    });

    var lineannotation = $('.snippet-code-addannotation .line-annotation');
    $.each(lineannotation,function(n,element){
      var linenum = n + 1;
      $('#line-'+linenum+'-addannotation').hover(function(){
        $('#addannotation_'+linenum).show();
      },function(){
        $('#addannotation_'+linenum).hide();
      })
    })

});

//获取cookie
function getCookie(name) {
     var cookieValue = null;
     if (document.cookie && document.cookie !== '') {
         var cookies = document.cookie.split(';');
         for (var i = 0; i < cookies.length; i++) {
             var cookie = jQuery.trim(cookies[i]);
             // Does this cookie string begin with the name we want?
             if (cookie.substring(0, name.length + 1) === (name + '=')) {
                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                 break;
             }
         }
     }
     return cookieValue;
 }

//单项选择题提交答案
function answer_option_question(question_id){
        var question_id = question_id;
        var option_obj = document.getElementsByName('question-'+question_id+'-answers-check');
        var user_choices = ''
        for(var i=0; i< option_obj.length;i++){
              if(option_obj[i].checked) user_choices += option_obj[i].value
        }
        if(user_choices === ""){
            alert("选择不能为空");
            return
        }
        //获取cookie
        var csrftoken = getCookie('csrftoken');
        $.ajax({
            cache: false,
            type: "POST",
            url:"/qa/evaluate_answer/",
            data:{'choices':user_choices,'question_id':question_id},
            async: true,
             beforeSend: function(xhr, settings) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },

            success: function(data) {
                if(data.status === 'fail'){
                    if(data.msg === '用户未登录'){
                        window.location.href="/users/login/";
                    }else{
                        alert(data.msg)
                    }
                }else if(data.status === 'success'){
                    alert(data.msg);
                    $.each(option_obj,function () {
                        $(this).attr("disabled",true);
                    });
                    $('.question-'+question_id+'-standard-answer').show();
                    $('#js-question-'+question_id+'-answer-button').hide();
                }
            }
        });
}

// 用户提问
function add_question(question_obj_type, question_obj_id) {
    var content = $("#js-que-textarea").val();
    if(content === ""){
        alert("问题不能为空")
        return
    }
    //获取cookie
        var csrftoken = getCookie('csrftoken');
    $.ajax({
        cache: false,
        type: "POST",
        url:"/qa/new_question/",
        data:{'content':content,'obj_type':question_obj_type,'obj_id':question_obj_id},
        async: true,
        beforeSend:function(xhr, settings){
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function(data) {
            if(data.status === 'fail'){
                if(data.msg ==='用户未登录'){
                    window.location.href="/users/login/";
                }else{
                    alert(data.msg)
                }
            }else if(data.status === 'success'){
                window.location.reload();//刷新当前页面.
            }
        }
    });
}

// 问答题答案提交
function submit_answer(answer_obj_id) {
        var content = $("#js-ans-textarea-"+answer_obj_id).val();
        question_id = answer_obj_id;
        if(content === ""){
            alert("答案不能为空");
            return
        }
         //获取cookie
        var csrftoken = getCookie('csrftoken');
        $.ajax({
            cache: false,
            type: "POST",
            url:"/qa/new_answer/",
            data:{'content':content,'question_id':question_id},
            async: true,
            beforeSend:function(xhr, settings){
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data) {
                if(data.status === 'fail'){
                    if(data.msg === '用户未登录'){
                        window.location.href="/users/login/";
                    }else{
                        alert(data.msg)
                    }
                }else if(data.status === 'success'){
                   alert(data.msg)
                    window.location.reload();//刷新当前页面.
                }
            }
        });
    }

//提交注释
function submit_annotation(line_id,type) {
    var content = '';
    //用户未注释直接点击数字查看别人注释所产生的输入框
    if (type === 0){
        content = $("#js-anno-textarea-"+line_id+'-0').val();
        var object = $('#0_select_'+line_id).val();
    }else{
    //用户直接点击添加注释按钮产生的输入框
        content = $("#js-anno-textarea-"+line_id+'-1').val();
        var object = $('#1_select_'+line_id).val();
    }
    if(content === ""){
        alert("注释不能为空");
        return
    }
    //获取cookie
    var csrftoken = getCookie('csrftoken');
    // 判断是问题还是注释

    // 如果是注释
    console.log(object);
    if(object === 'annotation'){
            $.ajax({
            cache: false,
            type: "POST",
            url:"/operations/new_annotation/",
            data:{'content':content,'line_id':line_id},
            async: true,
            beforeSend:function(xhr, settings){
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data) {
                if(data.status === 'fail'){
                    if(data.msg === '用户未登录'){
                        window.location.href="/users/login/";
                    }else{
                        alert(data.msg)
                    }
                }else if(data.status ==='success'){
                    alert(data.msg);
                    $('.qtip-content .new_line_annotation_'+line_id).html('您已经成功添加了注释');
                    $('.line-'+line_id+'-num').before('<div class="spacelinenum"></div>');
                    $('.line-'+line_id+'-anno').before('<div class="spaceline">    //'+content+'</div>');
                    $('.line-'+line_id+'-addanno').before('<div class="spaceline"></div>');
                    var showbutton =  $('#show-'+ line_id+'-annotation');
                     showbutton.click();
                     showbutton.removeAttr('onclick');
                     showbutton.click();
                }
            }
        });
    }else{
        //如果是提问
         $.ajax({
        cache: false,
        type: "POST",
        url:"/qa/new_question/",
        data:{'content':content,'obj_type':'line','obj_id':line_id},
        async: true,
        beforeSend:function(xhr, settings){
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function(data) {
            if(data.status === 'fail'){
                if(data.msg ==='用户未登录'){
                    window.location.href="/users/login/";
                }else{
                    alert(data.msg)
                }
            }else if(data.status === 'success'){
                alert('提问成功');
                window.location.reload();//刷新当前页面.
            }
        }
    });
    }

}

 //为注释添加评论
function submit_comment(annotation_id,name) {
    var content = $("#js-comment-textarea-"+annotation_id).val();
    if (content === "") {
        alert("评论不能为空");
        return
    }
    //获取cookie
    var csrftoken = getCookie('csrftoken');
    $.ajax({
        cache: false,
        type: "POST",
        url: "/operations/new_comment/",
        data: {'content': content,"annotation_id":annotation_id},
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if (data.status === 'fail') {
                if (data.msg === '用户未登录') {
                    window.location.href = "/users/login/";
                } else {
                    alert(data.msg)
                }
            } else if (data.status === 'success') {
                alert('评论成功');
                $('#annotation-'+annotation_id+' .postcell #comments').prepend('<div class="comment"><div class="postcell">' + content + '<span class="pull-right"><a>' + name + '</a>--刚刚</span></div></div>')
                $('.new_comment_'+annotation_id).hide();
                $('#new_annotation_comment_'+annotation_id).show();
            }
        }
    })
}

 //为问题添加评论
function submit_question_comment(question_id,name) {
    var obj= $(".controls #js-que-comment-textarea-"+question_id);
    $.each(obj,function(){
        content = $(this).val()
        if(content !== ''){
            return false
        }
    });

    if (content === "") {
        alert("评论不能为空");
        return
    }
    //获取cookie
    var csrftoken = getCookie('csrftoken');
    $.ajax({
        cache: false,
        type: "POST",
        url: "/qa/new_question_comment/",
        data: {'content': content,"question_id":question_id},
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if (data.status === 'fail') {
                if (data.msg === '用户未登录') {
                    window.location.href = "/users/login/";
                } else {
                    alert(data.msg)
                }
            } else if (data.status === 'success') {
                alert('评论成功');
                var comment_obj = $('.postcell #question_'+question_id+'_comment');
                $.each(comment_obj,function(){
                    $(this).append('<div class="question_comment">'+content+'<span class="pull-right"><a>'+name+'</a>    评论于刚刚</span></div>')
                })
                $.each(obj,function() {
                    $(this).val()
                })

            }
        }
    })
}

// 显示已有注释的气泡弹窗
// $(function(){
//   $('.annotations-count').each(function(){
//     var lineid = $(this).attr('rel')
//     $(this).qtip({
//             content: {
//                 text: $('.line-'+ lineid+'-annotation')
//             },
//             position:{
//                 my:'left center',
//                 adjust: {
//                     x: 50
//                 }
//             },
//             show:'click',
//             hide: 'unfocus',
//             style: {
//                       widget: true,
//                       classes: 'qtip-bootstrap',
//                       width:330
//
//                   }
//          })
//   })
// });

// 添加代码注释的气泡弹窗
$(function(){
    $('.add_line_annotation').each(function(){
      var lineid = $(this).attr('rel');
    $(this).qtip({
            content: {
                    text: $('.new_line_annotation_'+ lineid )
                },
            position: {
                my:'left top',
                viewport: $(window),
                adjust: {
                    x: 30
                }
            },
            show: {
                event: 'click',
                solo: true // Only show one tooltip at a time
                },
            hide: 'unfocus',
            style: {
                      widget: true,
                      classes: 'qtip-bootstrap'
                  }
         });
       }).click(function(event) { event.preventDefault(); });
});

// 显示问题
$(function(){
    $.each($('#question .question'),function () {
        $(this).hide()
    })
  $.each($('#question .question:lt(5)'),function(){
    $(this).show();
  });
  var question_count = $('#question .question').length;
  if (question_count < 5 ) {
    $('.show-more-button').hide();
  }
});

// 显示更多问题
function show_more(){
  var visible_count = $('#question .question:visible').length-1;
  $.each($('#question .question:gt('+visible_count+'):lt(5)'),function(){
    $(this).show();
    $('#question .question:visible:last').css('margin-bottom','0px')
    if ($('#question .question:visible').length == $('#question .question').length ) {
      var que1 = $('#question .question:visible');
      if(que1.length >5){
         $('.hide-last-button').show();
      }

      $('.hide-button').show();
      $('.show-more-button').hide();
    }
  })
}
// 隐藏多余问题,只显示一个
function hide_question(){
  $.each($('#question .question:gt(0)'),function(){
    $('#question .question:visible:last').css('margin-bottom','0px');
    $(this).hide();
    $('.show-more-button').show();
    $('.hide-button').hide();
    $('.hide-last-button').hide();
  })
}

// 隐藏最后五个显示的问题问题
function hide_last_question(){
    var que = $('#question .question:visible');
    $('#question .question:visible').slice(que.length-5,que.length).hide();
    var que1 = $('#question .question:visible');
    if(que1.length < 5){
        $('.hide-last-button').hide();
        $('.show-more-button').show();
        $('.hide-button').hide();
    }
}

//显示一个问答题答案
function show_one_an(params){
  $.each($('#question-'+params+' #answers .answer:lt(1)'),function(){
    $(this).show();
   $('#question-'+params+' #answers .answer:visible:last').css('margin-bottom','0px');
  });
  var answer_count = $('#question-'+params+' #answers .answer').length;
  if (answer_count < 2 ) {
    $('.show-more-ans-button-'+params).hide();
  }
}

//显示更多答案
function show_more_ans(params){
  var visible_count = $('#question-'+params+' #answers:first .answer:visible').length;
  console.log(visible_count);
      $.each($('#question-'+params+' #answers:first .answer:gt('+visible_count+'):lt(3)'),function(){
            $(this).show();
            $('#question-'+params+' #answers .answer:visible:last').css('margin-bottom','0px');
            if ($('#question-'+params+' #answers .answer:visible').length === $('#question-'+params+' #answers .answer').length ) {
              $('.hide-ans-button-'+params).show();
              $('.show-more-ans-button-'+params).hide();
            }
          });
}

//隐藏多余答案
function hide_ans(params){
  $.each($('#question-'+params+' #answers .answer:gt(0)'),function(){
    $('#question-'+params+' #answers .answer:visible:last').css('margin-bottom','0px');
    $(this).hide();

  });
  $('.show-more-ans-button-'+params).show();
  $('.hide-ans-button-'+params).hide();
}

// 点赞功能
function add_vote(vote_type, vote_id,vote_value) {
     //获取cookie
    var csrftoken = getCookie('csrftoken');
    $.ajax({
      cache:false,
      type:"POST",
      url: '/operations/add_vote/',
      data:{'vote_id':vote_id, 'vote_type':vote_type, 'vote_value':vote_value},
      dataType: 'json',
      async: true,
      beforeSend:function(xhr, settings){
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success:function (data) {
           if(data.status === 'fail'){
                if(data.msg === '用户未登录'){
                    window.location.href="/users/login/";

                }else{
                    alert(data.msg);
                }
            }else if(data.status === 'success'){

               var obj = $('.'+vote_type+'-'+vote_id+'-vote-count');
               var count = $('.'+vote_type+'-'+vote_id+'-vote-count:first').text()
               if(data.info ==='cancel'){
                   $.each(obj,function(){
                       $(this).prev('a').css('border-bottom','15px solid #8c8686');
                        $(this).text(Number(count)+Number(data.value))
                       $(this).next('a').css('border-top','15px solid #8c8686');
                       })

               }else{
                   if(vote_value === 1){
                       $.each(obj,function(){
                           $(this).prev('a').css('border-bottom','15px solid #f4e20e');
                            $(this).text(Number(count)+1)
                       })

                   }else{
                     $.each(obj,function(){
                            $(this).text(Number(count)-1)
                            $(this).next('a').css('border-top','15px solid #f4e20e');
                       })
                   }
               }

            }
      }
    });
}

// 搜索选中当前页面所在树结构的位置
function getCurrentPath(file){
    event.preventDefault();
    $("#method_tree").jstree(true).search(file,false, false, '#j1_1');
}
// 获取链接李的属性
function getUrlParam(name) {
   var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
   var r = window.location.search.substr(1).match(reg); //匹配目标参数
   if (r !== null) return unescape(r[2]); return null; //返回参数值
  }

//显示注释
function show_annotation(line_id,user_id,linenum) {
    if(user_id==='None'){
        window.location.href="/users/login/";
    }
 var csrftoken = getCookie('csrftoken');
$.ajax({
  cache:false,
  type:"POST",
  url: '/operations/judge_user_annotation/',
  data:{'line_id':line_id, 'user_id':user_id},
  dataType: 'json',
  async: true,
  beforeSend:function(xhr, settings){
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
  },
  success:function (data) {
       if(data.status === 'fail'){
            if(data.msg === '用户未登录'){
                window.location.href="/users/login/";
            }else{
                alert(data.msg);
            }
        }else if(data.status === 'success_1'){
          $('#show-'+ line_id+'-annotation').removeAttr('onclick');
           $('#show-'+ line_id+'-annotation').qtip({
                    content: {
                        text: $('.line-'+ line_id+'-annotation')
                    },
                        position:{
                            at:'right center',
                            adjust: {
                                x: 30,


                            }
                        },
                        show:'click',
                        hide: 'unfocus',
                        style: {
                                  widget: true,
                                  classes: 'qtip-bootstrap',
                                  width:330
                              }
                 });
           $('#show-'+ line_id+'-annotation').click()
        }else if(data.status === 'success_2'){
                $('#addannotation_'+linenum).click()
       }
  }
});

}

// #修改注释
function edit_annotation(annotation_id,orgin_content){
            var new_content = $('#js-annotation-'+annotation_id+'-textarea').val();
            var old_content = orgin_content;
            if(new_content === old_content){
                alert('你没有修改注释')
                return
            }
             if(new_content === ''){
                alert('注释不能为空')
                 return
            }
            var csrftoken = getCookie('csrftoken');
           $.ajax({
            cache: false,
            type: "POST",
            url:"/operations/edit_annotation/",
            data:{'content':new_content, 'annotation_id': annotation_id},
            async: true,
            beforeSend:function(xhr, settings){
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data) {
                if(data.status === 'fail'){
                    if(data.msg ==='用户未登录'){
                        window.location.href="/users/login/";
                    }else{
                        alert(data.msg)
                    }
                }else if(data.status === 'success'){
                    $('#annotation-content-'+annotation_id).text(new_content);
                    $('.annotation-'+annotation_id+'-edit-form').hide();
                    $('#annotation-'+annotation_id+'-edit-button').show();
                    alert(data.msg);

                }
            }
        });
        }

//修改按钮
function edit_button(annotation_id){
    $('#annotation-content-'+annotation_id).hide()
    $('#annotation-'+annotation_id+'-edit-button').hide();
     $('.annotation-'+annotation_id+'-edit-form').show()
}