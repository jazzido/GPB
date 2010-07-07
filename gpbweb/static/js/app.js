// format integer
var pad = function(num, length) {
    var r = "" + num;
    while (r.length < length) {
        r = "0" + r;
    }
    return r;
};

$(document).ready(function() {
		      
		      var highLightSliderRange = function(slider, months_li, start, end) {
			  var i;
			  months_li.css('background-color', 'white');
			  for(i = start; i < end; i++) {
			      $(months_li[i]).css('background-color', '#eeeeee');
			  }
		      };

                      var showSliderPeriod = function(months_li, start, end) {
			  // mostrar el periodo indicado con el slider
			  var periodo = '';

			  var a = $('a', months_li[end - 1]);
			  var href = BASE_URL + a.attr('name');
			  periodo += a.html() + '/' + a.attr('name').split('/')[0];

			  if (end - start == 1) { 
			      $('#periodo-display a').html(periodo);
         		      $('#periodo-display a').attr('href', href);
			      return;
			  }
			  
			  periodo += ' → ';

			  a = $('a', months_li[start]);
			  href += '/' + a.attr('name');
			  periodo += a.html() + '/' + a.attr('name').split('/')[0];

			  $('#periodo-display a').html(periodo);
			  $('#periodo-display a').attr('href', href);

                      };

		      var sliderInit = false;
		      
		      var initSlider = function() {

			  var months_li = $('ul#months-menu li ul li');
			  var months_a  = $('ul#months-menu li ul li a');

			  // buscar los indices de los links correspondientes segun RANGO_FECHAS
			  var start_slider = $.inArray(RANGO_FECHAS.end.getUTCFullYear() + '/' + pad(RANGO_FECHAS.end.getUTCMonth() + 1, 2), 
						       $.map(months_a, function(m) { return $(m).attr('name'); }));
			  if (start_slider == -1) start_slider = 0;

			  var end_slider = $.inArray(RANGO_FECHAS.start.getUTCFullYear() + '/' + pad(RANGO_FECHAS.start.getUTCMonth() + 1, 2), 
						     $.map(months_a, function(m) { return $(m).attr('name'); }));

			  $('#slider').css('width', $('li.year').inject(0, function(acc) { return acc + $(this).width(); }));

			  $('#slider').slider({range: true, 
					       max: months_li.length,
					       min: 0,
					       values: [start_slider, end_slider + 1],
					       slide: function(event, ui) {
						   highLightSliderRange(this, months_li, ui.values[0], ui.values[1]);
                                                   showSliderPeriod(months_li, ui.values[0], ui.values[1]);
					       } 
					      });

			  $('#slider .ui-slider-handle:eq(0)').addClass('wResize');
			  $('#slider .ui-slider-handle:eq(1)').addClass('eResize');

			  highLightSliderRange($('#slider'), months_li, start_slider, end_slider+1);
			  showSliderPeriod(months_li, start_slider, end_slider+1);

			  sliderInit = true;
			  
		      };

		      $('#filtro-container button').click(function() {
							      $('#filtro').toggleClass('hide');
							      if(!$('filtro').hasClass('hide') && !sliderInit) 
								  initSlider();
							  });
		  });
