$(document).ready(function(){
	xsrf = getCookie("_xsrf");
	
	$('#logout').click(function(event){

		jQuery.ajax({
			url:'//localhost:8000/logout',
			type:'GET',
			data:{
				_xsrf: xsrf,
				user: document.user,
				logout: 'logout'
			},
			datatype: 'json',

			success: function(data,status,xhr){
				window.location.href='http://localhost:8000/login'
			}
		});	

	});
		
});

function getCookie(name){
	var c = document.cookie.match("\\b"+name+"=([^;]*)\\b");
	return c ? c[1]:undefined;
}

