$(function() {
  $('#menu-tip, #filter-tip').delay(2000).fadeOut('slow');
  $( "#price-slider" ).slider({
    range: true,
    min: 50,
    max: 300,
    values: [ 50, 300 ],
    slide: function( event, ui ) {
      $("#price-range").text( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
    }
  });
  $("#price-range").text( $( "#price-slider" ).slider( "values", 0 ) +
    " - " + $( "#price-slider" ).slider( "values", 1 ) );

  $( "#distance-slider" ).slider({
    range: true,
    min: 0,
    max: 10,
    values: [ 0, 10 ],
    slide: function( event, ui ) {
      $("#distance-range").text( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
    }
  });
  $("#distance-range").text( $( "#distance-slider" ).slider( "values", 0 ) +
    " - " + $( "#price-slider" ).slider( "values", 1 ) );
});