function weixinShareTimeline(title,desc,link,imgUrl){ 
	weixinShare('shareTimeline', title, desc, link, imgUrl);
}

function weixinShare(messageType, title, desc, link, imgUrl) {
	if (typeof WeixinJSBridge != "undefined") {
		WeixinApi.ready(function(Api) {
			var wxData = {
					"appId": "",
					"img_url":imgUrl,
					"link":link,
					"desc":desc,
					"title":title
			};

			var wxCallbacks = {
					fail : function(resp) {
						if (messageType == 'shareTimeline') {
							showAjaxModal('点击右上角的按钮分享到朋友圈');
						} else if (messageType == 'sendAppMessage'){
							showAjaxModal('点击右上角的按钮分享给朋友');
						}
					},
					confirm : function(resp) {
					},
			};
			if (messageType == 'shareTimeline')
				Api.shareToTimeline(wxData, wxCallbacks);
			else if (messageType == 'sendAppMessage')
				Api.shareToFriend(wxData, wxCallbacks);
		});
		if (messageType == 'shareTimeline') {
			showAjaxModal('点击右上角的按钮分享到朋友圈');
		} else if (messageType == 'sendAppMessage'){
			showAjaxModal('点击右上角的按钮分享给朋友');
		}
	} else {
		showAjaxModal('请先通过微信搜索公众号"ForBilliardFans", 添加"我为台球狂"为好友，通过微信分享 :)');
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