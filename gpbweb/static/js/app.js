$(document).ready(function() {
		      //		      $('#filtro').toggleClass('hide');
		      var sliderInit = false;
		      var initSlider = function() {
			  var months_li = $('ul#months-menu li ul li');
			  $('#slider').css('width', $('li.year').inject(0, function(acc) { return acc + $(this).width(); }));
			  $('#slider').slider({range: true, 
					       max: months_li.length,
					       min: 0,
					       //                         values: 
					       slide: function(event, ui) {
						   months_li.css('background-color', 'white');
						   for(i = ui.values[0]; i < ui.values[1]; i++) {
						       $(months_li[i]).css('background-color', '#eeeeee');
						   }
					       } 
					      });
			  $('#slider .ui-slider-handle:eq(0)').addClass('wResize');
			  $('#slider .ui-slider-handle:eq(1)').addClass('eResize');
			  sliderInit = true;
			  
		      };

		      $('#filtro-container button').click(function() {
							      $('#filtro').toggleClass('hide');
							      if(!$('filtro').hasClass('hide') && !sliderInit) 
								  initSlider();
							  });
		  });
