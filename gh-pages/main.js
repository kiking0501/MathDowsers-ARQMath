function askQuestion() {
    var question_data;
    function getQuestion(callback){
        $.getJSON('data/ARQMath/experiments/topics/ARQMath_2021/task1-topics-2021.json', function(data) {
            callback(data);
        });
    }
    getQuestion(function (data) {
        question_data = data;
    })
    function print() {
        console.log(question_data);
    }
    $(".q-text").show("slow");
    $(".res").hide();
}

$(document).ready(function() {
    $(".q-text").hide();
})