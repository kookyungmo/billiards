$(function(jQuery) {

        // mobile-tab 代码
        // mobile-tab 工具对象
        function MobileTab($tabs, $contents) {           
        	var _this = this;
        	this._$tabs = $tabs;
        	this.$contents = $contents;
        	/*注册点击事件*/
        	$tabs.on('click', '.tab-item', function(e) {
        		var $tabItem = $(this);
        		e.preventDefault();

        		if($tabItem.hasClass('active')) {
        			return;
        		}

        		$tabItem.addClass('active')
        			.siblings('.active').removeClass('active');

        		_this.showPanel($tabItem.find('a').attr('href'));
        	})
        	// 注册tab滑动事件
        	.on('touchmove', function(e) {        		
        		var touchLeft = e.originalEvent.changedTouches[0].pageX;

        		e.preventDefault();

        		_this.touchMove(touchLeft);

        	})
        	// 注册滑动初始化事件
        	.on('touchstart', function(e) {
        		var $this = $(this),
        			left = parseFloat($this.css('left').split('px')[0]),
        			touchLeft = e.originalEvent.changedTouches[0].pageX,
        			maxLeft = 0,
        			minLeft = $this.parent().width() - $this.width();    		

        		_this.touchStart(left, touchLeft, maxLeft, minLeft);
        	})
        	// 注册滑动结束事件
        	.on('touchend', function(e) {
        		_this.touchEnd();        		
        	});
        };

        $.extend(MobileTab.prototype, {
        	/**
        	 * 显示模块
        	 * @param  {string} selector 目标模块的选择器
        	 */
        	showPanel: function (selector) {
        		var $target = this.$contents.filter(selector);

        		this.$contents.each(function() {
        			$(this).removeClass('active');
        		});

        		$target.addClass('active');
        	},
        	/**
        	 * 注销MobileTap
        	 */
        	destroy: function() {
        		this._$tabs.off().data('mobileTab', false);
        	},
        	/**
        	 * _$tabs的left
        	 * @type {Number}
        	 */
        	_left: 0,
        	/**
        	 * 当前触点与document的相对x位置
        	 * @type {Number}
        	 */
        	_touchLeft: 0,
        	/**
        	 * _$tabs最大的left值
        	 * @type {Number}
        	 */
        	_maxLeft: 0,
        	/**
        	 * _$tabs最小的left值
        	 * @type {Number}
        	 */
        	_minLeft: 0,
        	/**
        	 * 滑动初始化
        	 * @param  {[type]} left      _$tabs的left
        	 * @param  {[type]} touchLeft 当前触点与document的相对x位置
        	 * @param  {[type]} maxLeft   _$tabs最大的left值
        	 * @param  {[type]} minLeft   _$tabs最小的left值
        	 */
        	touchStart: function(left, touchLeft, maxLeft, minLeft) {
        		this._left = left;
        		this._touchLeft = touchLeft;
        		this._maxLeft = maxLeft;
        		this._minLeft = minLeft;
        	},
        	/**
        	 * 滑动结束
        	 */
        	touchEnd: function() {
        		if(this._left < this._minLeft) {
        			this._$tabs.animate({left: this._minLeft}, 500);
        		}else if(this._left > this._maxLeft) {
        			this._$tabs.animate({left: this._maxLeft}, 500);
        		}
        	},
        	/**
        	 * 滑动中
        	 * @param  {[type]} touchLeft 当前触点与document的相对x位置
        	 */
        	touchMove: function(touchLeft) {
        		var scroll = (touchLeft - this._touchLeft);
        		this._touchLeft = touchLeft;
        		this._left = this._left + scroll;

        		this._$tabs.css('left', this._left);
        	}
        });

        // jquery插件
        $.fn.mobileTabs = function(option) {
        	var $this = this.eq(0), $tabContent = $('.mobile-content');
        	if(typeof option === 'string') {
        		$this.data('mobileTab') && $this.data('mobileTab')[option]();
        	}else {
        		$this.data('mobileTab') || $this.data('mobileeTab', new MobileTab($this, $tabContent));            		
        	}
        	return this;
        };
});

jQuery(function($) {
        $('#mobile-tabs').mobileTabs();

        $('img[data-src]').each(function() {
                var $this = $(this);
                $this.prop('src', $this.data('src'));
        });
        $(document).foundation();         
});

