$(document).ready(function(){
	xsrf = getCookie("_xsrf");

	setTimeout(addRoom,100);

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

	$('#createRoom').click(function(event){
		jQuery.ajax({
			url:'//localhost:8000/rooms',
			type:'POST',
			data:{
				_xsrf: xsrf,
				roomCnt:document.roomCnt,
				action:'add'
			},	
			dataType:'json',

			beforeSend: function(xhr,settings){
				$(event.target).attr('disabled','disabled');
			},
			success: function(data,status,xhr){
				window.location.href='http://localhost:8000/'
			}
		});
	});
});



//function requestRooms(){
//	jQuery.getJSON('//localhost:8000/qRoom')
	
//}

function getCookie(name){
	var c = document.cookie.match("\\b"+name+"=([^;]*)\\b");
	return c ? c[1]:undefined;
}
function addRoom(cnt){
	if(cnt==100){
		return;
	}
	var host = 'ws://localhost:8000/status'
	var websocket = new WebSocket(host);

	websocket.onopen = function(evt){ };
	websocket.onmessage = function(evt){
		$('#roomCnt').html($.parseJSON(evt.data)['roomCnt']);
	};
	websocket.onerror = function(evt){ };
}
function join(){
	
}

