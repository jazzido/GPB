$(function(){
	$('select#valueAA, select#valueBB').selectToUISlider({
		labels: 24
	});
	$('#timeline').hide();
	$("#filtro_fecha ul li a").click(function() {
		$("#timeline").slideToggle();
	});
});