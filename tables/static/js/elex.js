var color_dict = {
    DEM: 'rgb(0, 160, 220)',
    GOP: 'rgb(215, 22, 53)',
    LIB: 'green',
    Undecided: 'rgb(199, 200, 202)'
};
// var template = _.template(d3.select('#tooltip').html());

function opacity2014(dx) {
    if (dx === '12086') {
        var x = '12025';
    }
    else {
        var x = dx;
    }
    var max = 140000;
    if (R2014[x]['victory_votes']){
    return (((R2014[x]['victory_votes'])*1) / max) + .07;  
    }
    else {
     return 1;   
    } 
};
function winnerColor2014(dx) {
    if (dx === '12086') {
        var x = '12025';
    }
    else {
        var x = dx;
        }
    if ((R2014[x]['leading_gov']) === 'Crist'){
        return color_dict["DEM"] }
    else if ((R2014[x]['leading_gov']) === 'Scott') {
        return color_dict["GOP"] }
    else if ((R2014[x]['leading_gov']) === 'Wyllie') {
        return color_dict["LIB"] }
    else {
        return color_dict["Undecided"]
    };
};  


//looks for the county leader and returns their name.
function winner2014(x) {
if ((R2014[x]['leading_gov']) === 'Crist'){
        return "Crist" }
    else if ((R2014[x]['leading_gov']) === 'Scott') {
        return "Scott" }
    else if ((R2014[x]['leading_gov']) === 'Wyllie') {
        return "Wyllie" }
    else {
        return ""};
};  

function tooltipHide(d) {
    $(this).tooltip('hide');
}

//set up master svg
var height = 700, width=1140;
var svg_map = d3.select("#map")
    .append("svg")
//    .attr("style", "a.active span {background-color:#FFFF55;}")
    .attr("id", "svg_map")
    .attr("width", "100%")
    .attr("height", height)
    .attr("border", "1px")
    .attr("preserveAspectRatio", "xMinYMin meet")
    .attr('class', 'svg-content')
    .attr('viewBox', "0 0 1140 700");
var projection = d3.geo.albers()
    .center([6.5, 27.7])
    .rotate([90, 0])
    .parallels([20, 30])
    .scale(11*500)
    .translate([width / 2, height / 2]);
var path = d3.geo.path()
    .projection(projection);
var toolDepth = 0;
d3.json("js/elex_counties.json", function(error, fla) {
    svg_map.append("g")
        .attr('id', 'florida_map')
        .attr('transform', 'translate(250, 0)')
        .append("g")
        .attr("id", "map_paths")
        .attr("fill", "none")
        .selectAll("path")
          .data(topojson.feature(fla, fla.objects.fla_counties_cb_smallest).features)
          .enter()
          .append('path')
          .attr("name", function(d) { return d.properties.name })
          .attr("id", function(d) { return d.id})
          .attr("d", path)
          .attr("stroke", "black")
          .attr("stroke-width", '1')
          .attr('fill', function(d) {
              return winnerColor2014(d.id)
               })
          .attr('opacity', '1')
          .append('text')
              .attr("class", "place-label")
              .attr("transform", function(d) { return "translate(" + path.centroid(d) + ")"; })
              .attr("dy", ".35em")
              .text(function(d)  { return d.properties.name });

svg.selectAll(".place-label")
    .attr("x", function(d) { return d.geometry.coordinates[0] > -1 ? 6 : -6; })
    .style("text-anchor", function(d) { return d.geometry.coordinates[0] > -1 ? "start" : "end"; });

          // .attr('opacity', function(d) {
          //     return opacity2014(d.id)
          //      })
});

svg.selectAll(".place-label")
    .data(topojson.feature(fla, fla.objects.fla_counties_cb_smallest).features)
  .enter().append("text")
    .attr("class", "place-label")
    .attr("transform", function(d) { return "translate(" + projection(d.geometry.coordinates) + ")"; })
    .attr("dy", ".35em")
    .text(function(d) { return d.properties.name; });
// function getPosition(event)
// {
//   var x = event.x;
//   var y = event.y;

//   // x -= canvas.offsetLeft;
//   // y -= canvas.offsetTop;
//   alert("x:" + x + " y:" + y);
// }

// var canvas = document.getElementById("map");
// canvas.addEventListener("mousedown", getPosition, false);
