$(document).ready(function(){
    var paper = new Raphael('map', 800, 775.042);

    var counties2014 = {};

    //sets the map colors, opacity is determined later
    var color_dict = {
        DEM: '#072c63',
        GOP: '#9e0500',
        LIB: '#009900',
        Undecided: 'rgb(200, 200, 200)'
    };
    
    //basics on page load
    function init(){
        $('.tstamp').html(R2014.tstamp);
        show2014(12);
        // createCountyDOMObjects2008();
        createCountyDOMObjects2014(); 
    };

    //terniary operator for the if statement. this calculates the turnout. formula works a little differently for the statewide data.
    function turnout2014(x) {
        var vote = (x=='12') ? "stateVote" : "vcast";
        return (Math.round(((R2014[x][vote]) / (R2014[x]['registered'])) *100 ));
    };

    //show results for the 2014 map
    function show2014(FIPS) {
        if (R2014[FIPS]['pcount'] !== 0){
        $('.winner').text(winner2014(FIPS));
        $('.county_name12').text(R2014[FIPS].name);
        $('.winhed').show()
        }
        else {
        $('.winhed').hide()
        }
        if (FIPS == "12"){
            $('.vote_margin12').text(R2014['victory_comma']);
        }  else {
            $('.vote_margin12').text(R2014[FIPS].victory_votes_comma);
        }

        //changing the bolding (or check marks after the election) for the winners in each county on hover.
        if (R2014[FIPS].leading_gov === "Scott"){
            $('.gopname').css('font-weight', '900');
            $('.demname').css('font-weight', 'normal');
            $('.thirdname').css('font-weight', 'normal');
            $('.o_color').html('<div class="obama_less_25k"></div>');
            $('.r_color').html('<div class="winner_check_gop"></div>');
            // $('.r_color').html('<div class="mccain_less_25k"></div>');
            $('.t_color').html('<div class="third_less_25k"></div>');
        }
        if (R2014[FIPS].leading_gov === "Crist"){
            $('.gopname').css('font-weight', 'normal');
            $('.demname').css('font-weight', '900');
            $('.thirdname').css('font-weight', 'normal');
            // $('.o_color').html('<div class="winner_check_dem"></div>');
            $('.o_color').html('<div class="obama_less_25k"></div>');
            $('.r_color').html('<div class="mccain_less_25k"></div>');
            $('.t_color').html('<div class="third_less_25k"></div>');
        }
        if (R2014[FIPS].leading_gov === "Wyllie"){
            $('.gopname').css('font-weight', 'normal');
            $('.demname').css('font-weight', 'normal');
            $('.thirdname').css('font-weight', '900');
            $('.o_color').html('<div class="obama_less_25k"></div>');
            $('.r_color').html('<div class="mccain_less_25k"></div>');
            // $('.t_color').html('<div class="winner_check_third"></div>');
            $('.t_color').html('<div class="third_less_25k"></div>');
        }

        //county-specific turnout and precinct setup
        $('.precincts_total').text(R2014[FIPS].ptotal);
        $('.ppct').text(R2014[FIPS].ppct);
        $('.turnout_number').text(turnout2014(FIPS));

        // pres race setup
        $('.obama12').text(R2014[FIPS].dem_comma);
        $('.obama_pct').text(R2014[FIPS].dem_pct);
        $('.romney12').text(R2014[FIPS].gop_comma);
        $('.romney_pct').text(R2014[FIPS].gop_pct);
        $('.third12').text(R2014[FIPS].third_comma);
        $('.third_pct').text(R2014[FIPS].third_pct);
    };

    //the opacity is set based on the margin of victory (in votes, not percents, small north florida counties totally skew the percent margin.) the max is obama's largest margin of victory (broward county in 2008). the .04 normalizes the colors so they're saturated enough to be interesting.
    // function opacity(x) {
    //     var max = 254911;
    //     return (((R2008[x]['victory_votes_int'])*1) / max) + .05;   
    // };

    //2014 max is also in broward county.
    function opacity14(x) {
        var max = 140000;
        return (((R2014[x]['victory_votes'])*1) / max) + .07;   
    };

    //looks in the color dictionary to find the color for each county's winner.
    function winnerColor2014(x) {
    if ((R2014[x]['leading_gov']) === 'Crist'){
            return color_dict["DEM"] }
        else if ((R2014[x]['leading_gov']) === 'Scott') {
            return color_dict["GOP"] }
        else if ((R2014[x]['leading_gov']) === 'Wyllie') {
            return color_dict["LIB"] }
        else {
            return color_dict["Undecided"]};
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
    
	//builds the rapahel map objects for the 2014 counties.
    function createCountyDOMObjects2014() {
        for (sv in flMap) {
                    counties2014[sv] = paper.path(flMap[sv]).attr({
                    'fill-opacity': opacity14(sv),
                    'stroke': '#A5A5A5',
                    'stroke-width': .5,
                    'fill': winnerColor2014(sv),
                    'cursor': 'pointer'
                    })
                    .data({'tooltip': R2014[sv]['name'], 'fips': sv})
                    .hover(function(e){
                        $('#tooltip').css('display', 'block').html(this.data('tooltip'));
                         $('#map').mousemove(function (event) {
                            var mousetop = event.pageY - 24;
                            var mouseleft = event.pageX + 1;
                            // var mousetop = event.pageY + 10;
                            // var mouseleft = event.pageX + 10;
                            $('#tooltip').css('top', mousetop).css('left', mouseleft);
                        });
                        show2014(this.data('fips'));
                    }, function() { 
                        $('#tooltip').css('display', 'none');
                        show2014(12);
                    });
        };
    };

    init();

});