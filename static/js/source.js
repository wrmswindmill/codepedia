var flag = true;//左侧默认显示

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
var csrftoken = getCookie('csrftoken');


function show_annotation(file_id, line_num) {
    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/show_annotation/',
        data: { 'file_id': file_id, 'line_num': line_num },
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if (data.status === "success") {
                $(".show-info-panel").html(data.html_str);

                var left = ($(".left").width());
                if (flag) {
                    $(".codereading").css("width", "60%");
                } else {
                    var wid = $(".codereading").width();
                    $(".codereading").css("width", wid - (left * 2) + "px");
                }
                $(".right").removeClass("none");
            }

        }
    });
}

// FIXME
function show_issue(file_id, line_num, issue_id_type) {

    //发送问题id，返回问题内容
    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/show_issue/',
        data: { 'file_id': file_id, 'line_num': line_num, 'issue_id_type': issue_id_type },
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {

            $(".show-info-panel").html(data.html_str);

            var left = ($(".left").width());
            if (flag) {
                $(".codereading").css("width", "60%");
            } else {
                var wid = $(".codereading").width();
                $(".codereading").css("width", wid - (left * 2) + "px");
            }
            $(".right").removeClass("none");
        }
    });
}

function add_vote(type, id, num) {
    // alert(1111)
}

function submit_answer(issue_id) {
    // 获取问题的内容
    console.log(issue_id)
    var content = $("input[name='question_" + issue_id + "']:checked").val()
    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/add_answer/',
        data: { 'content': content, 'issue_id': issue_id },
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if (data.status === 'success') {
                alert(data.msg)
            } else {
                alert(data.msg)
            }
        }
    });
}


function add_comment_action(item, id, type) {
    var content = $("#writetext_" + id).val();
    console.log(content);
    //发送一个ajax请求
    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/add_comment/',
        data: { 'object_id': id, 'type': type, "content": content },
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if (data.status === 'success') {
                var username = data.username;
                show_new_comment(item, content, username);
            } else {
                alert(data.msg);
            }
        }
    });
}

//添加评论
function show_new_comment(item, content, username) {
    var txt = $(item).siblings(".writetext").val();
    if (txt == "") {
        confirm("请输入评论内容");
        return;
    }
    var html = "";
    html += "<div class=\"comment-item\">";
    html += "<p class=\"comment-con\">" + content + "</p>";
    html += "<p class=\"comment-name\">----<a href=\"javascript:void(0)\">" + username + "</a></p></div>";
    $(item).parents(".comment-btn").before(html);
    $(item).parents(".comment-btn").find(".comment-write").addClass("none");
    $(item).parents(".comment-btn").find("#addcom").removeClass("none");
    $(item).siblings(".writetext").val("");
}


function show_add_annotation(item) {
    $(item).siblings("#addno-panel").show();
}

function add_annotation(file_id, line_num) {
    //$("#annotation").html("------您将在此处为第" + line_num + "行代码添加注释或者问题-------")
    // 获取当前是注释还是问题
    var select_context = "#addno-select-" + line_num + " option:selected";
    var selectValue = $(select_context).text();  //获取选中的项

    var text_context = "#addno-text-" + line_num;
    var content = $(text_context).val();
    if (content.trim().length == 0) {
        alert("内容不能为空")
        return;
    }

    if (selectValue == "注释") {
        // 向addAnnatation中发请求
        submint_annotation(file_id, line_num, content);
    } else {
        submint_question(file_id, line_num, content);
    }
}

function submint_annotation(file_id, line_num, content) {
    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/add_annotation/',
        data: { 'file_id': file_id, 'linenum': line_num, 'content': content },
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if (data.status == 'success') {
                console.log(11111);
                // 因为可能注释或问题没有值的时候，不会为该代码块添加html代码，所以首先判断
                // 然后将注释数+1
                var codeopration_anno_div = $("#codeopration_anno_" + line_num).html()
                if (codeopration_anno_div.trim().length == 0) {
                    var str = '<span id="annonums_' + line_num + '" class="annonums" onclick="show_annotation(' + file_id + ',' + line_num + ')">';
                    str += '1</span>';
                    $("#codeopration_anno_" + line_num).html(str);
                } else {
                    var annonum_before = $("#annonums_" + line_num).text();
                    $("#annonums_" + line_num).html(parseInt(annonum_before) + 1);
                }
            }
            alert(data.msg);
        }
    });
}


function submint_question(file_id, line_num, content) {
    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/add_question/',
        data: { 'file_id': file_id, 'linenum': line_num, 'content': content },
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if (data.status == 'success') {

                var codeopration_anno_div = $("#codeopration_question_" + line_num).html()
                if (codeopration_anno_div.trim().length == 0) {
                    var str = '<span id="questionums_' + line_num + '" class="questionnums" onclick="show_annotation(' + file_id + ',' + line_num + ')">';
                    str += '1</span>'
                    $("#codeopration_question_" + line_num).html(str);
                } else {
                    var question_before = $("#questionums_" + line_num).text();
                    $("#questionums_" + line_num).html(parseInt(question_before) + 1);
                }
            }
            alert(data.msg);
        }
    });
}

function search_symbol(args, ev) {
    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/show_method_info/',
        data: { 'args': args },
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if (data.status === 'success') {
                var obj = data.msg;
                var context = "<p class='search-title'>搜索结果</p><div class='resultform'>";
                console.log(obj);
                for (let i = 0; i < obj.length; i++) {
                    var filePath = obj[i]['path'];
                    var filePathTag = "<a href=\"/projects" + filePath + "\" target='_blank' class='re-path'>" + filePath + "</a>";
                    var code = window.atob(obj[i]['line'])
                    var lineno = obj[i]['lineno']
                    var codeTag = "<a href=\"/projects" + filePath + "#L" + lineno + "\" target='_blank'>" + code + "</a>";
                    context += "<div class='result-line'><span class='fl'>" + (i + 1) + ".  </span>" + filePathTag + "&nbsp;&nbsp;&nbsp;&nbsp;" + codeTag + "</div>";
                }
                context += "</div>";
                // console.log(context);
                $("#search_response").html(context);

                ev = ev || window.event;
                console.log('x=' + ev.clientX + ',' + 'y=' + ev.clientY)

                var mousePos = mouseCoords(ev);

                $("#search_response").css("top", mousePos.y);
                $("#search_response").css("left", mousePos.x);
                $("#search_response").show();
                ev.stopPropagation();
            }
        }
    });
}



function show_navigation(project_path, file_path) {

    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/show_navigation/',
        data: { 'project_path': project_path, 'file_path': file_path },
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },

        success: function (data) {
            if (data.status === 'success') {
                var content = "";
                var obj = data.msg;
                console.log(obj);
                for (let i = 0; i < obj.length; i++) {
                    var type = obj[i][0];
                    var str = '';
                    str += "<div id=" + type + ">";
                    str += "<div class='tags'>" + type + "</div>";
                    if (obj.length > 1) {
                        var items = obj[i][1];
                        for (let j = 0; j < items.length; j++) {
                            var name = items[j][0];
                            var linenum = items[j][1];
                            str += "<a class='def' href='#L" + linenum + "'>" + name + "</a><br>" + "</div>";
                        }
                    }
                    str += "</div>";
                    content += str;
                }
                // document.getElementById("annotation").style.display="block";
                $("#annotation").html(content)
            }
            else {
                $("#annotation").html(data.msg)
            }
        }
    });
}

function show_currentLine(linenum) {
    document.getElementById("code_" + linenum).style.backgroundColor = '#f1efec';
    document.getElementById("addanno_" + linenum).style.visibility = 'visible';
}

function hide_currentLine(linenum) {
    document.getElementById("code_" + linenum).style.backgroundColor = 'white';
    document.getElementById("addanno_" + linenum).style.visibility = 'hidden';
}

$(function () {
    $("body").click(function (event) {
        //点击页面隐藏弹出框
        if ($(event.target).parents().attr("class") == "addno-panel" || $(event.target).attr("id") == "addno-panel" || $(event.target).attr("class") == "put-option" || $(event.target).attr("class") == "put-text" || $(event.target).attr("id") == "submit" || $(event.target).attr("class") == "addanno-img") {
            return;
        }
        $(".addno-panel").hide();
        //alert($(event.target).attr("class"));
        $("#search_response").hide();
    })
    $("#filelist-content .item").click(function () {
        if ($(this).siblings(".sub-item").length > 0 && $(this).attr("show") == "0") {
            $(this).siblings(".sub-item").show();
            $(this).attr("show", "1");
        } else if ($(this).attr("show") == "1") {
            $(this).siblings(".sub-item").hide();
            $(this).attr("show", "0");
        }
    })

    $(".left-tab li").click(function () {
        $(".left-tab li").removeClass("active");
        $(this).addClass("active");
        $(".left-rightlist").hide();

        $(".left-rightlist").eq($(this).index()).show();

        if (flag == false) {
            $(".codereading").css("width", "80%");
            $(".left").animate({ "width": "20%" }, 1000);
        }

    })

    /*隐藏左侧部分*/
    $(".hideleft").click(function () {
        var wid = $(".left").width();
        $(".left").animate({ "width": "70px" }, 800);
        $(".left-tab li").removeClass("active");
        $(".codereading").width(parseInt($(".codereading").width()) + wid);
        flag = false;
    })

    $(".up").bind("click", function () {
        var count = $(this).siblings(".question-count").html();
        alert(11111)
        console.log(count)

        if ($(this).siblings(".down").hasClass("active")) {
            $(".up,.down").removeClass("active");
            $(this).siblings(".question-count").html(parseInt(count) + 1);
        } else {
            if ($(this).hasClass("active")) {
                $(this).removeClass("active");
                $(this).siblings(".question-count").html(parseInt(count) - 1);
            } else {
                $(this).siblings(".down").removeClass("active");
                $(this).addClass("active");
                $(this).siblings(".question-count").html(parseInt(count) + 1);
            }
        }
    })

    $(".down").bind("click", function () {
        var count = $(this).siblings(".question-count").html();

        if ($(this).siblings(".up").hasClass("active")) {
            $(".up,.down").removeClass("active");
            $(this).siblings(".question-count").html(parseInt(count) - 1);
        } else {
            if ($(this).hasClass("active")) {
                $(this).removeClass("active");
                $(this).siblings(".question-count").html(parseInt(count) + 1);
            } else {
                $(this).siblings(".down").removeClass("active");
                $(this).addClass("active");
                $(this).siblings(".question-count").html(parseInt(count) - 1);
            }
        }
    })
    $(".up-s").bind("click", function () {
        var count = $(this).siblings(".question-count").html();
        if ($(this).siblings(".down-s").hasClass("active")) {
            $(".up-s,.down-s").removeClass("active");
            $(this).siblings(".question-count").html(parseInt(count) + 1);
        } else {
            if ($(this).hasClass("active")) {
                $(this).removeClass("active");
                $(this).siblings(".question-count").html(parseInt(count) - 1);
            } else {
                $(this).siblings(".down-s").removeClass("active");
                $(this).addClass("active");
                $(this).siblings(".question-count").html(parseInt(count) + 1);
            }
        }
    })
    $(".down-s").bind("click", function () {
        var count = $(this).siblings(".question-count").html();

        if ($(this).siblings(".up-s").hasClass("active")) {
            $(".up-s,.down-s").removeClass("active");
            $(this).siblings(".question-count").html(parseInt(count) - 1);
        } else {
            if ($(this).hasClass("active")) {
                $(this).removeClass("active");
                $(this).siblings(".question-count").html(parseInt(count) + 1);
            } else {
                $(this).siblings(".down-s").removeClass("active");
                $(this).addClass("active");
                $(this).siblings(".question-count").html(parseInt(count) - 1);
            }
        }
    })

    //滚动codepanel隐藏搜索结果
    $(".codereading").scroll(function () {
        $("#search_response").hide();
    })
})
function addcomments(item) {
    $(item).siblings(".comment-write").removeClass("none");
    $(item).addClass("none");
}

function cancelcom(item) {
    $(item).parents(".comment-write").siblings("#addcom").removeClass("none");
    $(item).parents(".comment-write").addClass("none");
}

//隐藏右侧部分
function colserightpanel() {
    if (flag) {
        $(".codereading").css("width", "80%");
    } else {
        var rightwid = $(".right").width();
        var codewid = $(".codereading").width();
        $(".codereading").css("width", parseInt(codewid) + parseInt(rightwid));
    }
    $(".right").addClass("none");
}
function mouseCoords(ev) {
    console.log(ev);
    // debugger;
    if (ev.pageX || ev.pageY) {
        return {
            x: ev.pageX,
            y: ev.pageY
        };
    }
    return {
        x: ev.clientX + document.body.scrollLeft - document.body.clientLeft,
        y: ev.clientY + document.body.scrollTop - document.body.clientTop
    };
}