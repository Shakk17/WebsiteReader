if (/\/consent\/\?toURL\=/.test(document.location.href))
{
	document.cookie = "notice_preferences=2:";
	
	setTimeout(function(){
		document.location.toString().replace(/^.*?\?/, '').replace(/#.*$/, '').split('&').forEach(function(e, i){
			e = decodeURIComponent(e).split('=');
			
			if (e[0] == 'toURL')
				document.location.href = e[1];
		});
	}, 1000);
}