/**
 * Copyright (C) 2012 Axel Bodart.
 *
 * This work is distributed under the conditions of the Creative Commons
 * Attribution-Share Alike 3.0 Licence. This means you are free:
 * to Share - to copy, distribute and transmit the work
 * to Remix - to adapt the work

 * Under the following conditions:
 * * Attribution. You must attribute the work by stating your use of KanjiVG in
 *    your own copyright header and linking to KanjiVG's website
 *    (http://kanjivg.tagaini.net)
 * * Share Alike. If you alter, transform, or build upon this work, you may
 *    distribute the resulting work only under the same or similar license to this
 *    one.
 *
 * See http://creativecommons.org/licenses/by-sa/3.0/ for more details.
 */
KanjiViewer = {
    initialize:function (divName, strokeWidth, fontSize, zoomFactor, displayOrders, colorGroups, kanji) {
        this.paper = new Raphael(divName, '100%', '100%');
        this.strokeWidth = strokeWidth;
        this.fontSize = fontSize;
        this.displayOrders = displayOrders;
        this.colorGroups = colorGroups;
        this.kanji = kanji;
        this.fetchNeeded = true;
        this.setZoom(zoomFactor);
        this.draw();
    },
    setZoom:function (zoomFactor) {
        this.paper.setViewBox(0, 0, 109, 109);
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
        if (kanji != this.kanji) {
            this.kanji = kanji;
            this.fetchNeeded = true;
        }
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
            });
            jQuery.ajax({
                url:'kanjivg/kanji/0' + this.kanji.charCodeAt(0).toString(16) + '.svg',
                dataType:'xml',
                success:function (results) {
                    parent.fetchNeeded = false;
                    parent.xml = results;
                    parent.drawKanji();
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
                        });
                    }
                }
            });
        } else {
            this.drawKanji();
        }
    },
    createStroke:function (stroke, color) {
        stroke = this.paper.path(jQuery(stroke).attr('d'));
        stroke['initialColor'] = color;
        stroke.attr({
            'stroke':color,
            'stroke-width':this.strokeWidth,
            'stroke-linecap':'round',
            'stroke-linejoin':'round'
        });
        return stroke;
    },
    drawKanji:function () {
        var parent = this;
        this.paper.clear();
        Raphael.getColor.reset();
        groups = jQuery(this.xml).find('svg > g > g > g');
        if (!this.colorGroups || groups.length == 0) {
            jQuery(this.xml).find('path').each(function () {
                color = Raphael.getColor();
                stroke = parent.createStroke(this, color);
                stroke.hover(
                        function () {
                            this.attr({
                                'stroke':'black'
                            });
                        },
                        function () {
                            this.attr({
                                'stroke':this['initialColor']
                            });
                        }
                );
            });
        } else {
            groups.each(function () {
                color = Raphael.getColor();
                parent.paper.setStart();
                jQuery(this).find('path').each(function () {
                    stroke = parent.createStroke(this, color);
                });
                var set = parent.paper.setFinish();
                set.hover(
                        function () {
                            set.attr({
                                'stroke':'black'
                            });
                        },
                        function () {
                            set.attr({
                                'stroke':this['initialColor']
                            });
                        }
                );
            });
        }
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
            });
            if (!parent.displayOrders) {
                order.hide();
            }
        });
    }
};
