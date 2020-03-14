(function() {
	var url = document.location.href,
		is_dailymotion = false,
		is_dailybuzz = false;
	
	if (url.indexOf('dailymotion.com/embed') > -1)
		is_dailymotion = true;
	else if (url.indexOf('dailybuzz.nl/buzz/embed') > -1)
		is_dailybuzz = true;
	
	
	function searchEmbeds() {
		setTimeout(function() {
			
			// dailymotion.com iframe embeds
			if (is_dailymotion) {
				document.querySelectorAll('.np_DialogConsent-accept:not(.idcac)').forEach(function(button) {
					button.className += " idcac";
					button.click();
				});
			}
			
			// dailybuzz.nl iframe embeds
			else if (is_dailybuzz) {
				document.querySelectorAll('.as-js-optin:not(.idcac)').forEach(function(button) {
					button.className += " idcac";
					button.click();
				});
			}
			
			else {
				// Twitter
				document.querySelectorAll('.twitter-tweet-rendered:not(.idcac)').forEach(function(e) {
					var button = e.shadowRoot.querySelector('.js-interstitial:not(.u-hidden) .js-cookieConsentButton');
					
					if (button) {
						e.className += " idcac";
						button.click();
					}
				});
			}
			
			searchEmbeds();
		}, 1000);
	}

	var start = setInterval(function() {
		var html = document.querySelector('html');
		
		if (!html || /idcae/.test(html.className))
			return;
		
		html.className += ' idcae';
		searchEmbeds();
		clearInterval(start);
	}, 500);
})();