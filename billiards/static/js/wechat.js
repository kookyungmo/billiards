function weixinShareTimeline(title,desc,link,imgUrl){ 
    weixinShare('shareTimeline', title, desc, link, imgUrl);
}

function weixinShare(messageType, title, desc, link, imgUrl) {
	if (typeof WeixinJSBridge != "undefined") {
		if (messageType == 'shareTimeline') {
			showAjaxModal('点击右上角的按钮分享到朋友圈');
		} else if (messageType == 'sendAppMessage'){
			showAjaxModal('点击右上角的按钮分享给朋友');
		}
	} else {
		showAjaxModal('请先通过微信搜索 pktaiqiu 添加我为台球狂为好友，通过微信分享抢台费 :)');
	}
}

function showAjaxModal(message) {
	$('#shareToWechat').foundation('reveal', 'open', {
	    url: WECHAT_SHARE_URL,
	    data: {text: message}
	});
}

function weixinSendAppMessage(title,desc,link,imgUrl){ 
    weixinShare('sendAppMessage', title, desc, link, imgUrl);
} 