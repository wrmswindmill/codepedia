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
    ev = window.event
    var mousePos = mouseCoords(ev)

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
                $("#commentPanel").css("top", mousePos.y);
                $("#commentPanel").css("left", mousePos.x+35);
                $("#loadCommentpanel").show();
            }else{
                alert(data.msg)
            }

        }
    });
}

// FIXME
function show_issue_question(file_id, line_num, issue_ids) {
    issueid_str=issue_ids.toString()
    ev = window.event
    var mousePos = mouseCoords(ev)
    //发送问题id，返回问题内容
    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/show_issue_question/',
        data: { 'file_id': file_id, 'line_num': line_num, 'issue_ids': issueid_str},
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if(data.status=='success'){
                $("#loadQuestionpanel").html(data.html_str);
                if (data.issueAnswers) {
                    //字符串转换成整型数组
                    var dataStrArr = issueid_str.substring(1, issueid_str.length - 1).split(",")
                    var issue_ids = dataStrArr.map(function (data) {
                        return +data;
                    });
                    //
                    issueAnswers = JSON.parse(data.issueAnswers);
                    issueStandardAnswers = JSON.parse(data.issueStandardAnswers);

                    let count = 0
                    for (let i = 0; i < issue_ids.length; i++) {
                        issue_id = issue_ids[i]
      
                        if (issue_id == issueAnswers[count].fields.issue) {
                            var radios = document.getElementsByName("issue_" + issue_id)
                            user_answer = issueAnswers[0].fields.content;
                            standard_answer = issueStandardAnswers[0].fields.choice_position;
                            if (user_answer == standard_answer) {
                                radios[user_answer - 1].parentNode.style.color = "green";
                            } else {
                                radios[parseInt(user_answer) - 1].parentNode.style.color = "red";
                                radios[parseInt(standard_answer) - 1].parentNode.style.color = "green";
                            }
                            document.getElementById("submit_onechoice_" + issue_id).style.display = "None";
                            count = count + 1
                        }
                    }
                }
                $("#questionPanel").css("top", mousePos.y);
                $("#questionPanel").css("left", mousePos.x - 400);
                $("#loadQuestionpanel").show()
            }else{
                alert(data.msg)
            }    
        }
    });
}

function add_vote(type, id, num) {
    // alert(1111)
}

function submit_onechoice_issue(issue_id) {
    // 获取问题的内容
    var content = $("input[name='issue_" + issue_id + "']:checked").val()
    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/add_issue_answer/',
        data: { 'content': content, 'issue_id': issue_id },
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if (data.status === 'success') {
                var radios = document.getElementsByName("issue_" + issue_id)
                var choose = parseInt(content) - 1
                if (content == data.standAnswer){
                    radios[choose].parentNode.style.color = "green";               
                }else{
                    radios[choose].parentNode.style.color = "red";
                    radios[parseInt(data.standAnswer)-1].parentNode.style.color = "green";
                }
                document.getElementById("submit_onechoice_"+issue_id).style.display="None";
            } else {
                alert(data.msg)
            }
        }
    });
}


function add_comment_action(item, id, type) {
    var content = $("#writetext_" + id).val();
    if (content == "") {
        confirm("请输入评论内容");
        return;
    }
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

function add_question_answer(item,question_id) {
    // 获取回答的内容
    var content = $("#responseInput_" + question_id).val();
    if (content == "") {
        confirm("请输入回答内容");
        return;
    }
    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/add_question_answer/',
        data: { 'question_id': question_id,"content": content},
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if (data.status === 'success') {
                var username = data.username;
                show_new_question_answer(item, content, username);
            } else {
                alert(data.msg);
            }
        }
    });
}

function show_new_question_answer(item, content, username) {

    var html = '<div class="comments clearfix"><div class="fl"><img src="/static/image/users/default.png" width="45px" height="45px" class="radius" /></div>'
    html += '<div class="fl comments-right">'
    html += '<div class="question-comment">';
    html += '<p><span class="comments-name">' + username+'</span><span class="font-12 color-grey-c">10分钟前</span></p>';
    html += '<div class="comments-content">'+content+'</div>';
    html += '</div></div></div>'

    $(item).parents(".responsePanel").before(html);
    $(item).parent().siblings(".responseInput").val("");
}


function add_annotation(item,file_id, line_num) {
    // 获取当前是注释还是问题
    var selectValue = $(item).siblings(".put-select").find(".active").html().trim();
    var text_context = "#addno-text-" + file_id+"-"+line_num;
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
                // 因为可能注释或问题没有值的时候，不会为该代码块添加html代码，所以首先判断
                // 然后将注释数+1
                var codeopration_anno_div = $("#codeopration_anno_"+file_id+"_" + line_num).html()
                if (codeopration_anno_div.trim().length == 0) {
                    var str = '<span id="annonums_' + line_num + '" class="annonums" onclick="show_annotation(' + file_id + ',' + line_num + ')">';
                    // str += '1</span>';
                    str +='</span>';
                    $("#codeopration_anno_" + +file_id + "_" + line_num).html(str);
                } 
                // else {
                //     var annonum_before = $("#annonums_" + line_num).text();
                //     $("#annonums_" + line_num).html(parseInt(annonum_before) + 1);
                // }
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
                var codeopration_anno_div = $("#codeopration_question_" + file_id + "_" + line_num).html()
                if (codeopration_anno_div.trim().length == 0) {
                    var str = '<span id="questionums_' + line_num + '" class="questionnums" onclick="show_issue_question(' + file_id + ',' + line_num + ',[])">';
                    // str += '1</span>'
                    str += '</span>'
                    $("#codeopration_question_" + file_id + "_" + line_num).html(str);
                } 
                // else {
                //     var question_before = $("#questionums_" + line_num).text();
                //     $("#questionums_" + line_num).html(parseInt(question_before) + 1);
                // }
            }
            alert(data.msg);
        }
    });
}

function search_symbol(args) {

    ev = event || window.event
    var mousePos = mouseCoords(ev)

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
                // console.log(context);
                $("#search_response").css("top", mousePos.y);
                $("#search_response").css("left", mousePos.x);
                $("#search_response").html(data.html_str);
                $("#search_response").show();
                // ev.stopPropagation();
            }
        }
    });
}


navigation_map = new Map()

function show_navigation() {
    // 首先要获取当前打开的标签页，或者也可以获取当前的路径
    // 获取当前的项目名称
    var file_path=document.getElementsByClassName("filename")[0].innerHTML;
    var project_path="Notes"
    if( navigation_map.has(project_path+file_path)){
        content = navigation_map.get(project_path + file_path);
        $("#structure-context").html(content)
        return;
    }
    
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
                var file_id = data.file_id
                for (let i = 0; i < obj.length; i++) {
                    var type = obj[i][0];
                    var str = '';
                    str += "<div id=" + type + ">";
                    if(i==0){
                        str += "<div class='tags clearfix'><span style='float: left;'>" + type + "</span></div>";
                    }else{
                        str += "<div class='tags'>" + type + "</div>";
                    }

                    if (obj.length > 1) {
                        var items = obj[i][1];
                        for (let j = 0; j < items.length; j++) {
                            var name = items[j][0];
                            var linenum = items[j][1];
                            str += "<a class='def' href='#"+file_id+"_L" + linenum + "'>" + name + "</a><br>" + "</div>";
                        }
                    }
                    str += "</div>";
                    content += str;
                }
                // document.getElementById("annotation").style.display="block";
                navigation_map.set(project_path + file_path, content)
                $("#structure-context").html(content)
            }
            else {
                navigation_map.set(project_path + file_path, "")
                $("#structure-context").html("")
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
        // alert("left-tab li")
        $(".left-tab li").removeClass("active");
        $(this).addClass("active");
        $(".left-rightlist").hide();

        $(".left-rightlist").eq($(this).index()).show();

        if (flag == false) {
            $("#right_code").css("width", "80%");
            $(".left").animate({ "width": "20%" }, 1000);
        }

    })

    /*隐藏左侧部分*/
    $(".hideleft").click(function () {
        var wid = $(".left").width();
        $(".left").animate({ "width": "70px" }, 800);
        $(".left-tab li").removeClass("active");
        $("#right_code").width(parseInt($("#right_code").width()) + wid);
        flag = false;
    })


    //滚动codepanel隐藏搜索结果
    $("#right_code").scroll(function () {
        $("#search_response").hide();
    })

    $(".addno-panel").click(function (event) {
        event.stopPropagation();
    })

    $(".addanno").live("click",function (event) {
        $(".addno-panel").hide();
        $(this).siblings(".addno-panel").show();
        $(".addanno").find("i").removeClass("color-dark-57").addClass("color-grey-c");
        $(this).find("i").removeClass("color-grey-c").addClass("color-dark-57");
        event.stopPropagation();
    })

    $("body").click(function () { 
        $(".addno-panel").hide(); 
        $(".source-addno-panel").remove()
        $(".addanno").find("i").removeClass("color-dark-57").addClass("color-grey-c"); 
    })

    $("body").on('click', '.addno-panel', function(e) {
        e.stopPropagation();
    });

    $("#loadCommentpanel").on('click', '#commentPanel', function (e) {
        e.stopPropagation();
    });

    $("#loadQuestionpanel").on('click', '#questionPanel', function (e) {
        e.stopPropagation();
    });

    //隐藏评论框
    $("#loadCommentpanel").click(function (event) {
        $("#loadCommentpanel").hide();
    })
    //隐藏问题框
    $("#loadQuestionpanel").click(function (event) {
        $("#loadQuestionpanel").hide();
    })
    //点击评论框里的内容，阻止冒泡
    $("#commentPanel").click(function (event) {
        event.stopPropagation();
    })
    //点击问题框里的内容，阻止冒泡
    $("#questionPanel").click(function (event) {
        event.stopPropagation();
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

    var tab_items = document.getElementsByClassName("tab_item");
    for (var i = 0; i < tab_items.length; i++) {
        // debugger;
        tab_items[i].className = tab_items[i].className.replace(" active", "");
    }

    document.getElementById("code_" + path).style.display = "block";
    document.getElementById("tab_" + path).style.display = "block";
    document.getElementById("tab_" + path).className += " active";

    document.getElementsByClassName("filename")[0].innerHTML = path_input;
    console.log(11111)
    if(!issue_map.has(path)){
        window.setTimeout(function () { $("#hotest_issue").html(issue_map[path]) }, 3000);
    }else{
        $("#hotest_issue").html(issue_map[path]);
    }
    show_navigation();
}
// 添加一个新的标签页，
// 如果标签页不存在，则创建一个新的标签页，然后调用open_tab
// 如果标签页已经存在，则打开对应的标签页
// 并调用open_tab
function add_tab(project_id,path,filename) {

    //需要将path处理一下，因为css样式中/以及.是不行的
    var path_input = path;
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
        li_tab_item.className = "tab_item";
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
                    // console.log(content);
                    div_codereading.innerHTML = content;
                }
                else {
                    div_codereading.innerHTML = "";
                }
            }
        });
        open_tab(path_input);
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
                if (data.status === 'success') {
                    issue_map[path] = data.html_str;
                }
                else {
                    issue_map[path] = ""
                }
            }
        });

        tabSet.add(path);
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

// 对应目录级别的addnoPanel
function show_next_addnoPanel(file_id){
    $("#addno-panel-"+file_id).show();
    event.stopPropagation();
}

//注入html代码
function inject_addnoPanel_html(item,file_id,linenum) {
    html_str =  '<div class="addno-panel source-addno-panel" style="display:block">'+
                    '<div class="trangle-op"></div>'+
                    '<div class="put-content">'+
                        '<p class="put-select clearfix" id="addno-select-'+linenum+'">'+
                        '<span class="active" onclick=\'$(this).siblings("span").removeClass("active");$(this).addClass("active");\'>注释</span>'+
                            '<span onclick=\'$(this).siblings("span").removeClass("active"); $(this).addClass("active");\'>问题</span>'+
                        '</p>'+
                        '<textarea id="addno-text-'+file_id+'-'+linenum+'" class="put-text" placeholder="输入注释或者问题"> </textarea>'+
                        '<a href="#" onclick="add_annotation(this,'+file_id+','+linenum+')" class="submit fr" id="submit">提交</a>'+
                    '</div>'+
                '</div>';
    $(item).after(html_str)
    ev = window.event
    ev.stopPropagation();
} 




function add_dir_annotation(item, file_id, line_num){
    // 获取当前是注释还是问题
    var selectValue = $(item).siblings(".put-select").find(".active").html().trim();
    var text_context = "#addno-text-" + file_id + "-" + line_num;
    var content = $(text_context).val();

    if (content.trim().length == 0) {
        alert("内容不能为空")
        return;
    }
    if (selectValue == "注释") {
        // 向addAnnatation中发请求
        submint_dir_annotation(file_id, line_num, content);
    } else {
        submint_dir_question(file_id, line_num, content);
    }
}


function submint_dir_annotation(file_id, line_num, content) {

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
                var value = $("#dir_anno_" + file_id).html()
                if (value.trim().length == 0) {
                    $("#dir_anno_" + +file_id).html(1);
                }else{
                    $("#dir_anno_" + +file_id).html(parseInt(value) + 1);
                }
            }
            alert(data.msg);
        }
    });
}


function submint_dir_question(file_id, line_num, content) {
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
                var value = $("#dir_question_" + file_id).html()
                if (value.trim().length == 0) {
                    $("#dir_question_" + +file_id).html(1);
                } else {
                    $("#dir_question_" + +file_id).html(parseInt(value) + 1);
                }
            }
            alert(data.msg);
        }
    });
}


function thumbsAnno(item,anno_id,vote_value) {
    // 获取当前的vote
    vote_tag = $(item).children("span").first()
    vote_before = parseInt(vote_tag.text())
    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/add_vote/',
        data: { 'vote_type': "annotation", 'object_id': anno_id, 'vote_value': vote_value },
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if (data.status == 'success') {
                value = data.value
                vote_tag.text(value+vote_before)
            }else{
                alert(data.msg);
            }
        }
    });


    // 更改当前的vote,默认+1
}

window.onload = function () {
    url = window.location.href;
    $.ajax({
        cache: false,
        type: "POST",
        url: '/operations/get_addtab_paras/',
        data: { 'url': url },
        dataType: 'json',
        async: true,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
            if (data.status === 'success') {
                add_tab(data.project_id, data.path, data.filename)
            }
        }
    });
}