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
                $("#loadCommentpanel").html(data.html_str);
                $("#loadCommentpanel").show(); 
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
    html += "<p>" + username+"</p>";
    html += "<span class=\"color-grey-des\">" + content+"</span></div>"
    // html += "<p class=\"comment-con\">" + content + "</p>";
    // html += "<p class=\"comment-name\">----<a href=\"javascript:void(0)\">" + username + "</a></p></div>";

    
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
    console.log(selectValue)

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



function show_navigation() {
    // 首先要获取当前打开的标签页，或者也可以获取当前的路径
    // 获取当前的项目名称
    var file_path=document.getElementsByClassName("filename")[0].innerHTML;
    var project_path="Notes"
    console.log(file_path)

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
                $("#structure-context").html(content)
            }
            else {
                $("#structure-context").html(data.msg)
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

var tabSet = new Set();
var issue_map = new Map();

function path_predeal(path){
    // path = path.replace('.', '');
    // path = path.replace('/', '_');
    path = path.split('.').join('');
    path = path.split('/').join('_');
    return path;
}

// 打开一个已经存在的标签页
// 注意这个还得将对应的路径更改了
function open_tab(path) {
    path_input=path
    path = path_predeal(path)

    var tabcontent = document.getElementsByClassName("codereading");
    for (var i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    var tab_items = document.getElementsByClassName("tab_items");
    console.log(tab_items.length)
    for (var i = 0; i < tab_items.length; i++) {
        // debugger;
        tab_items[i].className = tab_items[i].className.replace(" active", "");
    }

    document.getElementById("code_" + path).style.display = "block";
    document.getElementById("tab_" + path).style.display = "block";
    document.getElementById("tab_" + path).className += " active";

    document.getElementsByClassName("filename")[0].innerHTML = path_input
    $("#hotest_issue").html(issue_map[path])
}
// 添加一个新的标签页，
// 如果标签页不存在，则创建一个新的标签页，然后调用open_tab
// 如果标签页已经存在，则打开对应的标签页
// 并调用open_tab
function add_tab(project_id,path,filename) {
    //需要将path处理一下，因为css样式中/以及.是不行的
    var path_input = path;
    console.log(path_input)
    path = path_predeal(path)

    if (tabSet.has(path)) {
        open_tab(path)
    } else {
        var tab_tag = document.getElementsByClassName("tab_head")[0];
        //添加tab
        /*<li class="tab_item" id="tab_src_net_micode_notes_widget_NoteWidgetProvider">
            <a href="javascript:void(0)" onclick="open_tab('src_net_micode_notes_widget_NoteWidgetProvider')">NoteWidgetProvider.java</a>
            <a href="javascript:void(0)" onclick="close_tab('src_net_micode_notes_widget_NoteWidgetProvider')">&times</a>
        </li> */
        var li_tab_item = document.createElement("li")
        li_tab_item.className = "tab_items";
        li_tab_item.id = "tab_" + path;

        var tag_a1 = document.createElement("a");
        tag_a1.href ="javascript:void(0)";
        tag_a1.textContent = filename
        tag_a1.onclick = (function () {
            return function () {
                open_tab(path_input);
            }
        })();
        
        var tag_a2 = document.createElement("a")
        tag_a2.href = "javascript:void(0)";
        tag_a2.textContent = '×'  
        tag_a2.onclick = (function () {
            return function () {
                close_tab(path_input);
            }
        })();


        li_tab_item.appendChild(tag_a1)
        li_tab_item.appendChild(tag_a2)
        tab_tag.appendChild(li_tab_item)

        // 添加对应的code-reading的Element
        var div_code = document.getElementsByClassName("code_Area")[0]
        var div_codereading = document.createElement("div")

        div_codereading.id = "code_" + path;
        div_codereading.className = "codereading";
        div_code.appendChild(div_codereading)

        tabSet.add(path);
        console.log(path)
        open_tab(path_input);

        $.ajax({
            cache: false,
            type: "POST",
            url: '/operations/get_codereading_content/',
            data: { 'project_id': project_id, 'path': path_input },
            dataType: 'json',
            async: true,
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },

            success: function (data) {
                if (data.status === 'success') {
                    // 获取code-reading的内容，并填充到对应的code-reading的Element
                    var content = data.html_str
                    div_codereading.innerHTML = content;
                }
                else {
                    div_codereading.innerHTML = "";
                }
            }
        });
        
        // 填充hotest_question
        $.ajax({
            cache: false,
            type: "POST",
            url: '/operations/get_hotest_issues/',
            data: { 'project_id': project_id, 'path': path_input,"question_num":5 },
            dataType: 'json',
            async: true,
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function (data) {
                console.log(111111111);
                if (data.status === 'success') {
                    console.log(data.html_str);
                    issue_map[path] = data.html_str;
                    // document.getElementById("hotest_issue").innerHTML=data.html_str;
                }
                else {
                    issue_map[path] = ""
                }
            }
        });
    }
}
// 这里也可以更改为item，传入this
function close_tab(path) {
    // 将当前的当前Element的父节点isplay:none
    // 将对应的code-reading区域设置为display:none
    path = path_predeal(path)

    var element = document.getElementById("tab_" + path);
    var previosuElement = element.previousElementSibling;
    var nextElement = element.nextElementSibling;

    document.getElementById("code_" + path).remove()
    element.remove()
    tabSet.delete(path)

    // 如果该标签页有上一个标签，将此标签的上一个标签页打开
    if (previosuElement != undefined) {
        var path = previosuElement.id.substr(4);
        open_tab(path)
        return;
    }
    // 如果该标签页有下一个兄弟标签，将此标签的下一个标签页打开
    if (nextElement != undefined) {
        var path = nextElement.id.substr(4);
        open_tab(path);
        return;
    }
}