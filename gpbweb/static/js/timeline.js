$(function(){
	$('select#valueAA, select#valueBB').selectToUISlider({
		labels: 24, scale: false
	});
	$('#timeline').hide();
	$("#filtro_fecha ul li a").click(function() {
		$("#timeline").slideToggle();
	});
});