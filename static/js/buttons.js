//push button
$("#tempButton").click(function () {
  $.post("/push", function (data) {
    let msg = data["button"] == "True" ? "ON" : "OFF";
    $("#tempButton").text(`Button is : ${msg}`);
  });
});

//metric button
$("#metricButton").click(function () {
  $.post("/switchTemp", function (data) {
    let msg = data["metric"] == "celcius" ? "C" : "F";
    $("#metricButton").text(`Temperature is in :${msg}`);
  });
});

function validatePhoneNumber(input_str) {
  var re = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/im;

  return re.test(input_str);
}

// update submit
$("#submit-btn").click(function (e) {
  e.preventDefault();
  let maxTemp = $("#max-temp").val();
  let minTemp = $("#min-temp").val();
  let phoneNumber = $("#phone-number").val();
  let metric = $("#metric").val();
  $.post("/setData", {
    metric: metric,
    maxTemp: maxTemp,
    minTemp: minTemp,
    phoneNumber: phoneNumber,
  }).done(function (data) {
    alert("Successfully updated the temperature and phone number");
    $("#max-temp").val("");
    $("#min-temp").val("");
    $("#phone-number").val("");
    $("#metric").val("c");
  });
});

//scale button
$("#btn-scale-sm").click(function () {
  console.log("small");
  $("svg").attr("width", "500px");
  $("svg").attr("height", "500px");
});
$("#btn-scale-me").click(function () {
  $("svg").attr("width", "800px");
  $("svg").attr("height", "500px");
});
$("#btn-scale-lg").click(function () {
  $("svg").attr("width", "950px");
  $("svg").attr("height", "600px");
});
