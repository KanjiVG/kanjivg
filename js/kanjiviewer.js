KanjiViewer = {
	initialize:function (divName, strokeWidth, fontSize, zoomFactor, displayOrders, colorGroups, kanji) {
		this.paper = new Raphael(divName, '100%', '100%');
		this.strokeWidth = strokeWidth;
		this.fontSize = fontSize;
		this.zoomFactor = zoomFactor / 100;
		this.displayOrders = displayOrders;
		this.colorGroups = colorGroups;
		this.kanji = kanji;
		this.fetchNeeded = true;
		this.view = this.paper.setViewBox(0, 0, 109, 109);
		this.draw();
	},
	setZoom:function (zoom) {
		this.zoomFactor = zoom;
	},
	setStrokeWidth:function (strokeWidth) {
		this.strokeWidth = strokeWidth;
	},
	setFontSize:function (fontSize) {
		this.fontSize = fontSize;
	},
	setStrokeOrdersVisible:function (visible) {
		this.displayOrders = visible;
	},
	setColorGroups:function (colorGroups) {
		this.colorGroups = colorGroups;
	},
	setKanji:function (kanji) {
		this.kanji = kanji;
		this.fetchNeeded = true;
	},
	draw:function () {
		if (this.fetchNeeded && this.kanji != "") {
			var parent = this;
			this.paper.clear();
			loader = this.paper.text(0, 0, 'Loading ' + this.kanji);
			loader.attr({
						'x':50,
						'y':50,
						'fill':'black',
						'font-size':18,
						'text-anchor':'start'
					}
			);
			jQuery.ajax({
						url:'kanjivg/kanji/0' + this.kanji.charCodeAt(0).toString(16) + '.svg',
						dataType:'xml',
						success:function (results) {
							parent.fetchNeeded = false;
							parent.xml = results;
							parent.onKanjiFetched();
						},
						statusCode:{
							404:function () {
								parent.paper.clear();
								error = parent.paper.text(0, 0, parent.kanji + ' not found');
								error.attr({
											'x':50,
											'y':50,
											'fill':'black',
											'font-size':18,
											'text-anchor':'start'
										}
								);
							}
						}
					}
			);
		} else {
			this.onKanjiFetched();
		}

	},
	onKanjiFetched:function () {
		var parent = this;
		this.paper.clear();
		display = this.paper.set();
		display['strokes'] = this.paper.set();
		display['orders'] = this.paper.set();
		Raphael.getColor.reset();
		jQuery(this.xml).find('path').each(function () {
			color = Raphael.getColor();
			stroke = parent.paper.path(jQuery(this).attr('d'));
			stroke['initialColor'] = color;
			stroke.attr({
						'stroke':color,
						'stroke-width':parent.strokeWidth,
						'stroke-linecap':'round',
						'stroke-linejoin':'round'
					}
			);
			stroke.hover(
					function () {
						this.attr({'stroke':'black'});
					},
					function () {
						this.attr({'stroke':this['initialColor']});
					}
			);
			stroke.click(function () {
				parent.setKanji(parent.kanji);
				parent.draw();
			});
		});
		jQuery(this.xml).find('text').each(function () {
			color = Raphael.color('black');
			text = jQuery(this).text();
			transform = jQuery(this).attr('transform');
			x = transform.split(' ')[4];
			y = transform.split(' ')[5].replace(')', '');
			order = parent.paper.text(x, y, text);
			order.attr({
						'fill':color,
						'font-size':parent.fontSize
					}
			);
			if (!parent.displayOrders) {
				order.hide();
			}
		});
	}
};
