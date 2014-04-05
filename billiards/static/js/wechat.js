function weixinShareTimeline(title,desc,link,imgUrl){ 
    weixinShare('shareTimeline', title, desc, link, imgUrl);
}

function weixinShare(messageType, title, desc, link, imgUrl) {
	if (typeof WeixinJSBridge != "undefined") {
		WeixinJSBridge.invoke(messageType,{ 
		    "img_url":imgUrl, 
		    "link":link, 
		    "desc":desc, 
		    "title":title 
		}); 
	} else {
		$('#shareToWechat').foundation('reveal', 'open');
	}
}

function weixinSendAppMessage(title,desc,link,imgUrl){ 
    weixinShare('sendAppMessage', title, desc, link, imgUrl);
} 