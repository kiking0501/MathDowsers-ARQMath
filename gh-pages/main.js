function askQuestion() {
    var question_data;
    var topic_id;
    var arqmath_year;
    function getQuestion(callback){
        arqmath_year = 2020 + Math.floor(Math.random() * 2);
        $.getJSON('data/ARQMath/experiments/topics/ARQMath_2021/task1-topics-' + arqmath_year + '.json', function(data) {
            callback(data);
        });
    }
    getQuestion(function (data) {
        question_data = data;
        topic_id = getRandomKey(data);
        writeQuestion(reloadMathJax);
    });

    function getRandomKey(obj){
        var keys = Object.keys(obj);
        return keys[ keys.length * Math.random() << 0];
    }
    function writeQuestion(callback) {
        $("#qbox").hide();
        var qbox = $("#qbox-template").clone();
        qbox.removeAttr("id");
        qbox.find(".qyear").text(arqmath_year);
        qbox.find(".qtopic-id").text(topic_id);
        qbox.find(".qbox-title").find(".qtopic-text").html(question_data[topic_id]["Title"]);
        qbox.find(".qbox-body").html(question_data[topic_id]["Question"]);
        qbox.find(".qbox-tags").text(question_data[topic_id]["Tags"]);
        qbox.show();
        $("#qbox").find(".placeholder").html(qbox);
        $("#qbox").show("slow");
        callback();
    }
}

function closeQuestion() {
    $("#qbox").find(".placeholder").html("");
    $("#qbox").hide("fast");
}

function searchQuestion() {
    var arqmath_year = $("#qbox").find(".qyear").text();
    var topic_id = $("#qbox").find(".qtopic-id").text();
    window.open("/gh-pages/result.html?ARQMath_year=" + arqmath_year + "&topic_id=" + topic_id);
}

function reloadMathJax() {
  MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
}

$(document).ready(function() {
    $(".q-text").hide();
})

function cleanMathML(text) {
    return text.replace(
        'display="block"', 'display="inline"').replace(
        '<merror class="ltx_error undefined undefined">', "").replace(
        "</merror>", "").replace(
        '<merror class="ltx_ERROR undefined undefined">', "");
}

function writeResult(arqmath_year, topic_id) {

    var rbox = $(".rbox");
    rbox.find(".rbox-title").find(".qyear").text(arqmath_year);
    rbox.find(".rbox-title").find(".qtopic-id").text(topic_id);

    function getResultQuestion(callback){
        $.getJSON('../data/ARQMath/experiments/topics/ARQMath_2021/task1-topics-' + arqmath_year + '-slt.json', function(data) {
            callback(data);
        });
    }
    // getResultQuestion(function (data) {
    //     writeResultQuestion(data);
    // });

    function writeResultQuestion(question_data) {
        var qbox = $("#qbox-template").clone();
        qbox.removeAttr("id");
        qbox.find(".qbox-title").find(".qtopic-text").html(cleanMathML(question_data[topic_id]["Title"]));
        qbox.find(".qbox-body").html(cleanMathML(question_data[topic_id]["Question"]));
        qbox.find(".qbox-tags").text(question_data[topic_id]["Tags"]);
        qbox.show();
        rbox.find(".qtopic-text").html(cleanMathML(question_data[topic_id]["Title"]));
        rbox.find(".placeholder").html(qbox);
    }

    function getTerms(callback) {
        $.getJSON('../data/ARQMath/experiments/topics/ARQMath_2021/task1-termCount-' + arqmath_year + '-rewrite.json', function(data) {
            callback(data[topic_id]);
        });
    }
    getTerms(function (data) {
        var terms = getSortedItems(data);
        var html = "";
        for (let i = 0; i < terms.length; i++) {
            html += "<ul>";
            html += cleanMathML(terms[i][0]);

            if (terms[i][1] > 1) {
                html += " <span class='badge'>" + terms[i][1] + "</span>";
            }
            html += "</ul>";
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
