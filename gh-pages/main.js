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

function askQuestion(isInitial, target) {
    // isInitial: whether the qbox panel has been opened
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
        }
        if (isInitial || isRandom(target)) {
            // clear and rewrite the select panel
            writeSelectPanel(arqmath_year, data, Object.keys(data), function() {
                highlightOption(arqmath_year + "," + topic_id);
            });
        } else {
            // only highlight the option
            highlightOption(arqmath_year + "," + topic_id);
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
        qbox.find(".qtopic-text").html(question_data["Title"]);
        qbox.find(".qbox-body").html(question_data["Question"]);
        qbox.find(".qbox-tags").text(question_data["Tags"]);
        qbox.show();
        $("#qbox").find(".qbox-placeholder").html(qbox);
        if (isInitial) {
            $("#qbox").show("slow");
        }
        accessJson(
            'data/ARQMath/postpro_2021/task1_' + arqmath_year + '_topic_info.json',
            function(topic_info) {
                if (topic_id in topic_info) {

                    var q_info = topic_info[topic_id];
                    unifyTopicInfo(q_info);
                    qbox.find(".qcategory").text(
                        q_info["Dependency"] + ", " + q_info["Topic Type"] + ", " + q_info["Difficulty"]
                    );
                }
        });
        callback();
    }

}

function closeQuestion() {
    $("#qbox").find(".qbox-placeholder").html("");
    $("#qbox").hide("fast");
}

function searchQuestion() {
    var arqmath_year = $("#qbox").find(".qyear").text();
    var topic_id = $("#qbox").find(".qtopic-id").text();
    window.open("gh-pages/result.html?ARQMath_year=" + arqmath_year + "&topic_id=" + topic_id);
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
        option += " onclick='askQuestion(false, this.value)'"
        option += ">[" + arqmath_year + "," + q_keys[i] + "] ";
        option += q_data[q_keys[i]]["Title"].slice(0, 50) + "..." ;
        option += "</option>"
        select.append(option)
    }
    select.attr("size", Math.min(Math.max(q_keys.length,2),  20));
    $("#num-topics").text(q_keys.length);
    callback();
}

function highlightOption(val) {
    var select = $("#qbox").find(".qpanel-dropdown").find("select");
    select.val(val).change();
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
}
$(document).ready(function() {
    $(".q-text").hide();
})

function cleanMathML(text) {

    return text.replace(
        'display=\"block\"', 'display=\"inline\"').replace(
        '<merror class="ltx_error undefined undefined">', "").replace(
        "</merror>", "").replace(
        '<merror class="ltx_ERROR undefined undefined">', "");
}

function writeResult(arqmath_year, topic_id) {

    var rbox = $(".rbox");
    rbox.find(".qyear").text(arqmath_year);
    rbox.find(".qtopic-id").text(topic_id);

    function getResultQuestion(callback){
        accessJson('../data/ARQMath/experiments/topics/ARQMath_2021/task1-topics-' + arqmath_year + '-slt.json', callback);
    }
    // getResultQuestion(function (data) {
    //     writeResultQuestion(data);
    // });

    function writeResultQuestion(question_data) {
        var qbox = $("#qbox-template").clone();
        qbox.removeAttr("id");
        qbox.find(".qbox-title").find(".qtopic-text").html(cleanMathML(question_data[topic_id]["Title"]));
        qbox.find(".qbox-title").find(".qyear").text(arqmath_year);
        qbox.find(".qbox-title").find(".qtopic-id").text(topic_id);
        qbox.find(".qbox-body").html(cleanMathML(question_data[topic_id]["Question"]));
        qbox.find(".qbox-tags").text(question_data[topic_id]["Tags"]);
        qbox.show();
        rbox.find(".qtopic-text").html(cleanMathML(question_data[topic_id]["Title"]));
        rbox.find(".placeholder").html(qbox);
    }

    function getTerms(callback) {
        accessJson('../data/ARQMath/experiments/topics/ARQMath_2021/task1-termCount-' + arqmath_year + '-rewrite.json', callback);
    }
    getTerms(function (data) {
        var terms = getSortedItems(data[topic_id]);
        var html = "";
        for (let i = 0; i < terms.length; i++) {
            // html += "<ul>";
            html += "<div>";
            html += cleanMathML(terms[i][0]);

            if (terms[i][1] > 1) {
                html += " <span class='badge'>" + terms[i][1] + "</span>";
            }
            html += "</div>";
            // html += "</ul>";
            // if (i !== terms.length - 1) {
            //     html += ", ";
            // }

        }
        // html += "</h4>";
        $(".rbox").find(".rbox-keywords").html(html);
    })
    function getSortedItems(obj) {
        var items = Object.keys(obj).map(function(key) {
          return [key, obj[key]];
        });
        // Sort the array based on the second value than first value
        items.sort(function(a, b) {
          return a[1] !== b[1]? b[1] - a[1]: b[0] < a[0]? 1: -1;
        });
        return items;
    }
}

function toggleShowKeyword(container, target) {
    $(target).toggle("fast");
    $(container).find("i").toggleClass("fa-plus-circle fa-minus-circle");
}
