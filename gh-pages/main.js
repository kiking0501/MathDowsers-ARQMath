function askQuestion() {
    var question_data;
    var topic_id;
    function getQuestion(callback){
        $.getJSON('data/ARQMath/experiments/topics/ARQMath_2021/task1-topics-2021.json', function(data) {
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
        qbox.find(".qbox-title").find(".qtopic-id").text("[" + topic_id + "]");
        qbox.find(".qbox-title").find(".qtopic-text").html(question_data[topic_id]["Title"]);
        qbox.find(".qbox-body").html(question_data[topic_id]["Question"]);
        qbox.find(".qbox-tags").text(question_data[topic_id]["Tags"]);
        qbox.show();
        $("#qbox").find(".placeholder").html(qbox);
        $("#qbox").show("slow");
        callback();
    }

    function print() {
        console.log(topic_id);
    }
}

function closeQuestion() {
        $("#qbox").find(".placeholder").html("");
        $("#qbox").hide("fast");
    }

function reloadMathJax() {
  MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
}

$(document).ready(function() {
    $(".q-text").hide();
})