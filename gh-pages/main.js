var request_type = "get";

function accessJson(url, callback) {
    if (request_type === "get") {
        $.getJSON(url, function(data) {
            callback(data);
        }).fail( function(data) {
                    console.log(data);
                });
    } else if (request_type === "post") {
        $.post(url, "{}", function(data) {
            callback(data);
        }, "json");
    }
}

function accessFile(url, callback){
    $.ajax({
        url: url,
        type: 'get',
        success: function(data) {
            callback(data);
        },
        error: function() {
        }
    });
}

function getFormulaDisplayStyle() {
    return $("#formula-display-style").text();
}

function checkisLimitSize() {
    if ($("#hostSource").text() == "gitHub") {
        return true;
    } else {
        return false;
    }
}

/*
====================
/ Question Panel
====================
*/

function askQuestion(target) {
    // target: whether a question-id has been fixed or to be randomly generated later
    var topic_id;
    var arqmath_year;

    if (isRandom(target)) {
        arqmath_year = 2020;
        arqmath_year += Math.floor(Math.random() * 2);
        $("[name=arqmath-year").val([arqmath_year]);
        $(".qpanel-breakdown").find("button").removeClass("selected");
    } else {
        arqmath_year = target.split(",")[0];
        topic_id = target.split(",")[1];
    }
    function getQuestions(callback){
        var name = "task1-topics-" + arqmath_year;
        var formulaSuffix = ((getFormulaDisplayStyle() === "slt")? "-slt" : "");
        name += formulaSuffix;

        if (isRandom(target)) {
            // reading all questions
            accessJson(
                'data/ARQMath/experiments/topics/ARQMath_2021/' + name + '.json',
                callback);
        } else {
            // reading an individual question
            accessJson(
                'data/ARQMath/experiments/topics/ARQMath_2021/' + name + '/' + name + '-' + topic_id + '.json',
                callback)
        }
    }
    getQuestions(function (data) {
        // generate a question-id if not yet
        if (isRandom(target)) {
            topic_id = getRandomKey(data);
            // clear and rewrite the select panel
            writeSelectPanel(arqmath_year, data, Object.keys(data), function() {
                highlightOption(arqmath_year, topic_id);
            });
        } else {
            // only highlight the option
            highlightOption(arqmath_year, topic_id);
        }

        // write the specific question
        var question_data = data;
        if (isRandom(target)) {
            question_data = data[topic_id];
        }
        writeQuestion(question_data, reloadMathJax);
    });

    function getRandomKey(obj){
        var keys = Object.keys(obj);
        return keys[ keys.length * Math.random() << 0];
    }
    function isRandom(target) {
        return target == undefined;
    }

    function writeQuestion(question_data, callback) {
        var qbox = $("#qbox-template").clone();
        qbox.removeAttr("id");
        qbox.find(".qyear").text(arqmath_year);
        qbox.find(".qtopic-id").text(topic_id);
        qbox.find(".qtopic-text").html(cleanFormula(question_data["Title"]));
        qbox.find(".qbox-body").html(cleanFormula(question_data["Question"]));
        qbox.find(".qbox-tags").text(question_data["Tags"].split(",").join(" , "));
        qbox.show();
        $("#qbox").find(".qbox-placeholder").html(qbox);
        accessJson(
            'data/ARQMath/postpro_2021/task1_' + arqmath_year + '_topic_info.json',
            function(topic_info) {
                if (topic_id in topic_info) {

                    var q_info = topic_info[topic_id];
                    unifyTopicInfo(q_info);
                    qbox.find(".qcategory").text(
                        "(" + q_info["Dependency"] + ", " + q_info["Topic Type"] + ", " + q_info["Difficulty"] + ")"
                    );
                }
        });
        callback();
    }

}


function reloadMathJax() {
  MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
}

function writeSelectPanel(arqmath_year, q_data, q_keys, callback) {

    q_keys.sort(function(a, b) {
        var a_id = parseInt(a.split(".")[1]);
        var b_id = parseInt(b.split(".")[1]);
      return a_id - b_id;
    });

    var select = $("#qbox").find(".qpanel-dropdown").find("select");
    select.html("");
    for (var i = 0; i < q_keys.length; i++) {
        var option = '<option value="' + arqmath_year + "," + q_keys[i] + '"';
        option += " onclick='askQuestion(this.value)'"
        option += ">[" + arqmath_year + "," + q_keys[i] + "] ";
        option += q_data[q_keys[i]]["Title"].slice(0, 50) + "..." ;
        option += "</option>"
        select.append(option)
    }
    select.attr("size", Math.min(Math.max(q_keys.length,2),  20));
    $("#num-topics").text(q_keys.length);
    callback();
}

function highlightOption(arqmath_year, topic_id) {
    var select = $("#qbox").find(".qpanel-dropdown").find("select");
    select.val(arqmath_year + "," + topic_id).change();
    select.focus();
    $(".qpanel-placeholder").find(".qyear").text(arqmath_year);
    $(".qpanel-placeholder").find(".qtopic-id").text(topic_id);
    questionSelected(true);
}

function unifyTopicInfo(q_info) {
    function cleanInfoLabel(ori_label, target_label, obj) {
        if (ori_label in obj) {
            obj[target_label] = obj[ori_label];
        }
    }
    function cleanInfoValue(label, ori_value, target_value, obj) {
        if (obj[label] == ori_value) {
            obj[label] = target_value;
        }
    }
    cleanInfoLabel("Category", "Topic Type", q_info);
    cleanInfoLabel("TopicType", "Topic Type", q_info);
    cleanInfoLabel("Dependence", "Dependency", q_info);

    cleanInfoValue("Topic Type", "Calculation", "Computation", q_info);
    cleanInfoValue("Difficulty", "Low", "Easy", q_info);
}

function filterQuestion(btn) {

    if (typeof(btn) != undefined) {
        if ($(btn).hasClass("selected")) {
            $(btn).removeClass("selected");
        } else {
            $(btn).parent().parent().children().find("button").removeClass("selected");
            $(btn).addClass("selected");
        }
    }
    var selected = $(".qpanel-breakdown").find(".selected");
    var filter = {};
    for (var i = 0; i < selected.length; i++) {
        var select_btn = $(selected[i]);
        var label = $(select_btn.parent().parent().find(".grid-label")[0]).text();
        var value = select_btn.text();
        filter[label] = value;
    }
    var arqmath_year = $('[name="arqmath-year"]:checked').val();
    var name = "task1-topics-" + arqmath_year;
    var formulaSuffix = ((getFormulaDisplayStyle() === "slt")? "-slt" : "");
    name += formulaSuffix;
    accessJson(
        'data/ARQMath/experiments/topics/ARQMath_2021/' + name + '.json',
        function(data) {
            if (Object.keys(filter).length === 0) {
                writeSelectPanel(arqmath_year, data, Object.keys(data), function() {});
            } else {
                accessJson(
                    'data/ARQMath/postpro_2021/task1_' + arqmath_year + '_topic_info.json',
                    function(topic_info) {
                        var filtered_data = {};

                        for (var topic_id in topic_info) {
                            var q_info = topic_info[topic_id];
                            unifyTopicInfo(q_info);

                            var satisfy = true;
                            for (var fkey in filter) {
                                if (q_info[fkey] != filter[fkey]) {
                                    satisfy = false;
                                }
                            }
                            if (satisfy) {
                                filtered_data[topic_id] = data[topic_id];
                            }
                        }
                        writeSelectPanel(arqmath_year, filtered_data, Object.keys(filtered_data), function() {});
                    }
                )
            }
    });
}

function resetPanel() {
    $("[name=arqmath-year").val([2021]);
    $(".qpanel-breakdown").find("button").removeClass("selected");
    filterQuestion();
    questionSelected(false);
}
function cleanFormula(text) {
    if (getFormulaDisplayStyle() === "slt") {
        return text;
        // var mathml = $(text).find("merror").remove();
        // console.log("hey", mathml);
        // // $(mathml).remove("merror");
        // return mathml;
    }
    return text;
}


function questionSelected(flag) {
    if (!flag) {
        $("#questionIsSelected").html("");
        $(".qbox-placeholder").html("<h4 style='color:dimgrey'> No Selected Question. </h4>");
        $(".btn_view_question_run").prop("disabled", true);


        // initial state
        $("#btn_view_result").prop("disabled", true);
        $("#btn_view_separate_answers").prop("disabled", true);
        $("#resultIsLoaded").html("");
        $(".ajax-loader-gif").hide();

    } else {
        $("#questionIsSelected").html("<i class='fa fa-check'></i>");

        // question changed, need to disable
        $("#btn_view_result").prop("disabled", true);
        $("#btn_view_separate_answers").prop("disabled", true);
        $("#resultIsLoaded").html("");
    }
}

/*
====================
/ View Result
====================
*/

var topK = 20;

function viewResult() {
    var arqmath_year = $($("#qbox").find(".qyear")[0]).text();
    var topic_id = $($("#qbox").find(".qtopic-id")[0]).text();
    $("#btn_view_result").prop("disabled", false);
    openTab("view_result");
    writeResult(arqmath_year, topic_id);
}


function writeResult(arqmath_year, topic_id) {
    resultIsLoaded(false);
    $("#answer-rows").html("");
    $("#document-placeholder").html("");
    var runName = $(".rbox-dropdown").val();
    if (typeof runName == 'undefined') {
        runName = "post-duplicate";
    }
    var rbox = $(".rbox");
    rbox.find(".qyear").text(arqmath_year);
    rbox.find(".qtopic-id").text(topic_id);

    var qcategory = $($("#qbox").find(".qcategory")[0]).text();
    rbox.find(".qcategory").text(
        qcategory
    );

    rbox.find(".topic-title").html(
        $($("#qbox").find(".qtopic-text")[0]).html()
    )
    rbox.find(".topic-tags").html(
        $($("#qbox").find(".qbox-tags")[0]).html()
    )
    $("#ajax-loader-gif").show();

    function getResultTSV(callback) {
        accessFile('data/ARQMath/experiments/runs/simple-task1-topics-' + arqmath_year + '-' + runName + '.tsv', callback);
    }
    function getRelevancy(callback) {
        accessFile('data/ARQMath/experiments/qrels_official_' + arqmath_year + '/qrel_task1', callback);
    }
    function getDirectoryManifest(callback) {
        accessFile('data/ARQMath/prepro_2021/html-manifest.txt', callback);
    }

    getDirectoryManifest(function (str) {
        var lines = str.split('\n');
        var directory_path = 'data/ARQMath/html_minimal_2021';
        var directory_list = [];
        for (var i = 0; i < lines.length; i++) {
            splits = lines[i].split('\t');
            directory_list.push([splits[0], parseInt(splits[1]), parseInt(splits[2])]);
        }

        getRelevancy(function(str){
            lines = str.split('\n');
            var relevancy_dict = {};
            for (var i = 0; i < lines.length; i++) {
                splits = lines[i].split('\t');
                res_topic_id = splits[0];
                if (res_topic_id == topic_id) {
                    relevancy_dict[splits[2]] = parseInt(splits[3]);
                }
            }

            getResultTSV(function (str) {
                lines = str.split('\n');
                var topic_results = [];
                for (var i = 0; i < lines.length; i++) {
                    splits = lines[i].split('\t');
                    res_topic_id = splits[0];
                    if (res_topic_id == topic_id) {
                        topic_results.push(splits);
                    }
                }

                getHtmlFile(directory_list, relevancy_dict, topic_results);
            });

        });

    });
}

function getHtmlFile(directory_list, relevancy_dict, topic_results) {

    function checkDirectoryPath() {
        if (i < directory_list.length) {
            $.ajax({
                url: "data/ARQMath/html_minimal_2021/2010-2018_3patterns" + directory_list[i][0] + "/" + topic_results[rank][1] + "/" + topic_results[rank][1] + "_" + topic_results[rank][2] + ".html",
                type: 'get',
                success: function(data) {
                    thread2path[thread_id] = "data/ARQMath/html_minimal_2021" + directory_list[i][0];
                },
                error: function() {

                }
            });
        }
    }
    var thread2path = {};
    var relevancy_count = [0, 0, 0, 0, 0];
    if (checkisLimitSize()) {
        // Use for GitHub with Size Limit
        topK = 5;

        for (var rank = 0; rank < Math.min(topK, topic_results.length); rank++) {
            var thread_id = topic_results[rank][1];
            var answer_id = topic_results[rank][2];
            var relevancy = -1;
            if (answer_id in relevancy_dict) {
                relevancy = relevancy_dict[answer_id];
            }
            $.ajax({
                url: "data/ARQMath/html_minimal_2021/selected/" + thread_id + "_" + answer_id + ".html",
                type: 'get',
                async: false,
                success: function (doc_str) {
                    drawCard(rank, answer_id, thread_id, relevancy, doc_str);
                }
            });
        }

    } else {
        // Use for UW-CS homepage with all documents available

        for (var rank = 0; rank < Math.min(topK, topic_results.length); rank++) {
            var thread_id = topic_results[rank][1];
            var answer_id = topic_results[rank][2];
            var relevancy = -1;
            if (answer_id in relevancy_dict) {
                relevancy = relevancy_dict[answer_id];
            }
            if (!(thread_id in thread2path)) {
                for (var i = 0; i < directory_list.length; i++) {
                    if (!(thread_id in thread2path)) {
                        if ((parseInt(thread_id) >= directory_list[i][1]) && (parseInt(thread_id) <= directory_list[i][2])) {
                            $.ajax({
                                url: "data/ARQMath/html_minimal_2021/2010-2018_3patterns" + directory_list[i][0] + "/" + thread_id + "/" + thread_id + "_" + answer_id + ".html",
                                type: 'get',
                                async:false,
                                success: function (doc_str) {
                                    thread2path[thread_id] = "data/ARQMath/html_minimal_2021/2010-2018_3patterns" + directory_list[i][0];
                                    drawCard(rank, answer_id, thread_id, relevancy, doc_str);
                                }
                            });
                        }
                    }
                }
            } else {
                $.ajax({
                    url: thread2path[thread_id] + "/" + thread_id + "/" + thread_id + "_" + answer_id + ".html",
                    type: 'get',
                    async: false,
                    success: function (doc_str) {
                        drawCard(rank, answer_id, thread_id, relevancy, doc_str);
                    }
                })
            }

        }
    }

    function drawCard(rank, answer_id, thread_id, relevancy, doc_str) {

        var answer = $("#answer-abstract-template").clone();
        answer.attr("id", answer_id);
        answer.find(".answer-rank").text(rank + 1);
        answer.find(".answer-id").text(answer_id);
        answer.find(".thread-id").text(thread_id);
        answer.find(".relevancy-score").text(relevancy);
        if (relevancy == -1) {
            answer.find(".relevancy-label").html(
                "<span><em>(unjudged)</em></span>"
            );
        } else if (relevancy == 0) {
            answer.find(".relevancy-label").html(
                '<span class="label label-default">Irrelevant</span>'
            );
        } else if (relevancy == 1) {
            answer.find(".relevancy-label").html(
                '<span class="label label-primary">Low Relevance</span>'
            );
        } else if (relevancy == 2) {
            answer.find(".relevancy-label").html(
                '<span class="label label-info">Medium Relevance</span>'
            );
        } else if (relevancy == 3) {
            answer.find(".relevancy-label").html(
                '<span class="label label-success">High Relevance</span>'
            );
        }


        var doc_html = $('<div/>').html(doc_str).contents();
        answer.find(".answer-body").html(
            $(doc_html.find('#answer')[0]).html()
        );
        answer.find(".mse-link").attr(
            "href", "https://math.stackexchange.com/questions/" +
            doc_html.find("#question").attr("question_id")
        )

        answer.find(".answer-question-title").html(
            $(doc_html.find("#question-title").find("h1")[0]).html()
        )
        var tags = $(doc_html.find("#tags")[0]).find("span");
        for (var i = 0; i < tags.length; i++) {
            if (i == 0) {
                answer.find(".answer-question-tags").html($(tags[i]).html());
            } else {
                answer.find(".answer-question-tags").append("," + $(tags[i]).html())
            }
        }

        answer.find(".original-document").html(
            $(doc_html.find("#question-title").parent()).html()
        );
        answer.show();
        $("#answer-rows").append(answer.html());

        relevancy_count[relevancy + 1]++;
    }

    resultIsLoaded(true);
    $($(".answer-abstract-placeholder").find(".panel-heading")[0]).click();
    var badges = $(".display-counts").find(".badge");
    $("#label-HR").find(".badge").text(relevancy_count[4].toString());
    $("#label-R").find(".badge").text(relevancy_count[3].toString());
    $("#label-LR").find(".badge").text(relevancy_count[2].toString());
    $("#label-IR").find(".badge").text(relevancy_count[1].toString());
    $(".display-counts").find(".badge").show();
}


function resultIsLoaded(flag) {
    var labels = ["label-IR", "label-LR", "label-R", "label-HR"];
    for (var i = 0; i < labels.length; i++)
        updateRelevanceLabel($("#" + labels[i]), false);
    if (!flag) {
        $("#resultIsLoaded").html("");
        $("#btn_view_separate_answers").prop("disabled", true);
        $(".ajax-loader-gif").show();
        $(".document-placeholder").html("");
        $(".display-counts").find(".label").find(".badge").hide();
        $(".num-results").text("");

    } else {
        $("#resultIsLoaded").html("<i class='fa fa-check'></i>");
        $("#btn_view_separate_answers").prop("disabled", false);
        $(".ajax-loader-gif").hide();
        $(".num-results").text(topK.toString());

        // can only view tab after result loading
        $(".btn_view_result").prop("disabled", false);
        reloadMathJax();
    }
}


function selectAnswerDocument(btn) {
    function writeComment(src, target) {
        if ($.trim($(target.find("table").find("tbody")[0]).html()) == "") {
            src.html("N/A");
        } else {
            src.html(target);
        }
    }

    function writePostLink(src, target) {

        if ($.trim($(target.find("table").find("tbody")[0]).html()) == "") {
            src.html("N/A");
        } else {
            target.find("tr").each(function(ind, ele) {
                var td = $(ele).find("td:eq(0)")
                var original = td.html();
                td.html(
                    "<a href='https://math.stackexchange.com/questions/"
                    + td.attr("post_id")
                    + "' target='_blank'>"
                    + original
                    + "</a>"
                )
            });
            src.html(target);
        }
    }

    function numberRows($t) {
        $t.find("tr").each(function(ind, ele) {
            var original = $(ele).find("td:eq(0)").html();
            var number = "<span style='color:dimgrey'>[ " + (ind + 1) + " ]</span>"
            $(ele).find("td:eq(0)").html(number + original);
        });
    }

    $(".isViewing").css("color", "dimgrey");

    $(btn).find(".isViewing").css("color", "orange");

    // *** write Header ***
    var ans_doc = $("#document-template").clone();
    ans_doc.removeAttr("id");
    ans_doc.find(".answer-rank").text(
        $($(btn).find(".answer-rank")).text()
    );
    ans_doc.find(".answer-id").text(
        $($(btn).find(".answer-id")).text()
    );
    ans_doc.find(".mse-link").attr(
        "href", "https://math.stackexchange.com/questions/" +
        $($(btn).find(".thread-id")).text()
    );
    ans_doc.find(".relevancy-label").html(
        $($(btn).find(".relevancy-label")).html()
    );
    ans_doc.find(".relevancy-score").text(
        $($(btn).find(".relevancy-score")).text()
    );

    // *** write Body ***
    var doc_node = $($(btn).parent().parent().find(".original-document"));


    ans_doc.find(".answer-full-body").html(
        $($(btn).parent().find(".answer-body")[0]).html()
    );
    writeComment(
        ans_doc.find(".answer-comments"),
        $(doc_node.find("#answer-comments")[0])
    )
    numberRows(ans_doc.find(".answer-comments"));


    ans_doc.find(".question-title").html(
        $(doc_node.find("#question-title").find("h1")[0]).html()
    );
    ans_doc.find(".question-body").html(
        $(doc_node.find("#question")[0]).html()
    );
    ans_doc.find(".question-tags").html(
        $(doc_node.find("#tags")[0]).html()
    );
    writeComment(
        ans_doc.find(".question-comments"),
        $(doc_node.find("#question-comments")[0])
    );
    numberRows(ans_doc.find(".question-comments"));


    writePostLink(
        ans_doc.find(".duplicate-posts"),
       $(doc_node.find("#duplicate")[0])
    )
    numberRows(ans_doc.find(".duplicate-posts"));

    writePostLink(
        ans_doc.find(".related-posts"),
        $(doc_node.find("#related")[0])
    )
    numberRows(ans_doc.find(".related-posts"));

    ans_doc.show();
    $(".document-placeholder").html(ans_doc.html());
}


function toggleRelevance(btn) {
    $(".switch input").prop("checked", !$(".switch input").is(":checked"));
    if ($(".switch input").is(":checked")) {
        $(btn).parent().find(".switch-text").text("ON");
        $(".relevancy-label").show();
    } else {
        $(btn).parent().find(".switch-text").text("OFF");
        $(".relevancy-label").hide();
    }
}


function viewSeperateAnswers(){
    var w = window.open(
            "gh-pages/popup_answers.html",
            "popUpAnswerLists?_=" + (new Date().getTime()),
            "width=" + Math.max(600, Math.round(screen.width * 0.3)) + ", height=" + Math.round(screen.height * 0.8)+ ", scrollbars=yes");
    var arqmath_year = $($("#qbox").find(".qyear")[0]).text();
    var topic_id = $($("#qbox").find(".qtopic-id")[0]).text();
    var runName = $(".rbox-dropdown").val();

    w.document.title = "[ARQMath " + arqmath_year + ", " + topic_id + "] " + runName;
    $(w).on('load', function(){
        w.document.title = "[ARQMath " + arqmath_year + ", " + topic_id + "] " + runName;
        var body = $(w.document.body);
        var list_answers = $("#answer-rows").clone();
        list_answers.find(".answer-details").show();
        list_answers.find(".panel-heading").attr("onclick", "");
        body.html(list_answers.html());
    });

}


function updateRelevanceLabel(label, update_active) {
    if (update_active) {
        label.find(".badge").css("color", "orange");
        // label.css("outline", "3px solid orange");
        // label.css("background-color", "#f1f1f1");
        label.css("color", "rgb(255,229,180)");
    } else {
        label.find(".badge").css("color", "");
        // label.css("outline", "");
        // label.css("background-color", "");
        label.css("color", "");
    }
    label.attr("active", update_active.toString());
}
function filterByRelevance(relevancy_score) {
    function checkTextBoolean(text) {
        if (text == "false") return false;
        return true;
    }
    var labels = ["label-IR", "label-LR", "label-R", "label-HR"];

    var update_active = !(checkTextBoolean($("#" + labels[relevancy_score]).attr("active")));
    updateRelevanceLabel($("#" + labels[relevancy_score]), update_active);



    var totalActive = update_active;
    for (var i = 0; i < labels; i++) {
        totalActive |= checkTextBoolean($("#" + labels[i]).attr("active"));
    }

    if (!totalActive) {
        $("#answer-rows").find(".answer-abstract-panel").each(function(ind, div) {
            $(div).css("display", "inherit");
        });
    } else {

        $("#answer-rows").find(".answer-abstract-panel").each(function(ind, div) {

            var ind_score = parseInt($($(div).find(".relevancy-score")).text());

            if (ind_score >= 0 && checkTextBoolean($("#" + labels[ind_score]).attr("active"))) {
                $(div).css("display", "inherit");
            } else {
                $(div).hide();
            }
        });
    }
}

function toggleExpand(container, target) {
    $(target).toggle("fast");
    $(container).find("i").toggleClass("fa-plus-circle fa-minus-circle");
}
