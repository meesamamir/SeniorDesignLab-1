const times = [...Array(300).keys()]; // time: X axis
let tempsC = [];
let tempsF = [];

let dataset = "";

let datasetC = tempsC.map(function (item, i) {
  return [times[i], item];
});

let datasetF = tempsF.map(function (item, i) {
  return [times[i], item];
});

//graph property that is unchanged
let svg = d3.select("svg"),
  margin = 200,
  width = svg.attr("width") - margin,
  height = svg.attr("height") - margin;

// Title
svg
  .append("text")
  .attr("x", width / 2 + 100)
  .attr("y", 100)
  .attr("text-anchor", "middle")
  .style("font-family", "Helvetica")
  .style("font-size", 20)
  .text("Temperature Graph");

// X label
svg
  .append("text")
  .attr("x", width / 2 + 100)
  .attr("y", height - 15 + 150)
  .attr("text-anchor", "middle")
  .style("font-size", 12)
  .text("Time");

// Y label
svg
  .append("text")
  .attr("text-anchor", "middle")
  .attr("transform", "translate(60," + (height - 50) + ")rotate(-90)")
  .style("font-size", 12)
  .text("Temperature");

let g = svg.append("g").attr("transform", "translate(" + 100 + "," + 100 + ")");
let xScale = d3.scaleLinear().domain([0, 300]).range([0, width]);
g.append("g")
  .attr("transform", "translate(0," + height + ")")
  .call(d3.axisBottom(xScale));
let yScale = d3.scaleLinear().domain([10, 50]).range([height, 0]);
g.append("g").attr("class", "yaxis").call(d3.axisLeft(yScale));

// fetch and update display and graph every second
function update() {
  // recallibrate the length & width for size in case of

  // ajax call to get the latest temp
  let requests = $.get("/temp");
  requests.done(function (result) {
    //perform queue is == 300, if less just insert at 0
    if (tempsC.length == 300) {
      tempsC.pop();
      tempsF.pop();
    }
    tempsC.unshift(result["tempC"]);
    tempsF.unshift(result["tempF"]);

    datasetC = tempsC.map(function (item, i) {
      return [times[i], item];
    });
    datasetF = tempsF.map(function (item, i) {
      return [times[i], item];
    });

    // if sensor or switch is off, update the display to that (check switch then check sensor)
    // also if sensor or switch is off, data goes missing (maybe update the database value to something like 999)

    //10-50c or 50-122 f
    displayCondition =
      result["sensor"] === "True" && result["switch"] === "True";
    console.log(displayCondition);
    if (displayCondition) {
      if (result["metric"] == "celcius") {
        $("#tempDisplay").text(result["tempC"] + "°" + "C");
        yScale.domain([-10, 50]);
        g.selectAll("g.yaxis").call(d3.axisLeft(yScale));
        dataset = datasetC;
      } else {
        $("#tempDisplay").text(result["tempF"] + "°" + "F");
        yScale.domain([50, 112]);
        g.selectAll("g.yaxis").call(d3.axisLeft(yScale));
        dataset = datasetF;
      }
    } else if (result["switch"] == "False") {
      $("#tempDisplay").text("Switch is Off");
    } else {
      $("#tempDisplay").text("Sensor Unplugged");
    }

    // Drawing line
    let line = d3
      .line()
      .defined(function (d) {
        return d[1] !== "False";
      })
      .x(function (d) {
        return xScale(d[0]);
      })
      .y(function (d) {
        return yScale(d[1]);
      })
      .curve(d3.curveMonotoneX);

    svg.select(".line").remove();

    svg
      .append("path")
      .datum(dataset)
      .attr("class", "line")
      .attr("transform", "translate(" + 100 + "," + 100 + ")")
      .attr("d", line)
      .style("fill", "none")
      .style("stroke", "darkblue")
      .style("stroke-width", "1");
  });
}
setInterval(update, 1000);
