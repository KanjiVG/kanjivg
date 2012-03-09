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
        this.refreshKanji();
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
        if (kanji != this.kanji && kanji != '' && kanji != undefined) {
            this.kanji = kanji;
            this.fetchNeeded = true;
        }
    },
    refreshKanji:function () {
        if (this.fetchNeeded && this.kanji != "") {
            var parent = this;
            this.paper.clear();
            var loader = this.paper.text(0, 0, 'Loading ' + this.kanji);
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
                        var error = parent.paper.text(0, 0, parent.kanji + ' not found');
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
    createStroke:function (path, color) {
        var stroke = this.paper.path(jQuery(path).attr('d'));
        stroke['initialColor'] = color;
        stroke.attr({
            'stroke':color,
            'stroke-width':this.strokeWidth,
            'stroke-linecap':'round',
            'stroke-linejoin':'round'
        });
        return stroke;
    },
    createHover:function (stroke) {
        var onEnteredAnim = Raphael.animation({stroke:'black'}, 300);
        var onLeftAnim = Raphael.animation({stroke:stroke['initialColor']}, 300);
        stroke.hover(
                function () {
                    this.animate(onEnteredAnim);
                }, function () {
                    this.animate(onLeftAnim);
                }
        );
    },
    createHovers:function (strokes) {
        var parent = this;
        var onEnteredAnim = Raphael.animation({stroke:'black'}, 300);
        var onLeftAnim = Raphael.animation({stroke:strokes[0]['initialColor']}, 300);
        for (var i = 0; i < strokes.length; i++) {
            var stroke = strokes[i];
            stroke.hover(
                    function () {
                        for (var j = 0; j < strokes.length; j++) {
                            stroke = strokes[j];
                            stroke.attr({
                                'cursor':'pointer'
                            });
                            stroke.animate(onEnteredAnim);
                        }
                    },
                    function () {
                        for (var j = 0; j < strokes.length; j++) {
                            stroke = strokes[j];
                            stroke.animate(onLeftAnim);
                        }
                    }
            );
            stroke.click(function () {
                parent.setKanji(strokes['element']);
                parent.refreshKanji();
            });
        }
    },
    drawKanji:function () {
        var parent = this;
        this.paper.clear();
        Raphael.getColor.reset();
        var groups = jQuery(this.xml).find('svg > g > g > g');
        if (!this.colorGroups || groups.length == 0) {
            jQuery(this.xml).find('path').each(function () {
                var color = Raphael.getColor();
                var stroke = parent.createStroke(this, color);
                parent.createHover(stroke);
            });
        } else {
            groups.each(function () {
                var color = Raphael.getColor();
                parent.paper.setStart();
                jQuery(this).find('path').each(function () {
                    parent.createStroke(this, color);
                });
                var set = parent.paper.setFinish();
                var element = jQuery(this).attr('kvg:element');
                if (element == undefined) {
                    var inners = jQuery(this).find('g');
                    for (var i = 0; i < inners.length; i++) {
                        element = jQuery(inners[i]).attr('kvg:element');
                        if (element !== undefined) {
                            set['element'] = element;
                            break;
                        }
                    }
                } else {
                    set['element'] = element;
                }
                parent.createHovers(set);
            });
        }
        jQuery(this.xml).find('text').each(function () {
            var color = Raphael.color('#808080');
            var text = jQuery(this).text();
            var transform = jQuery(this).attr('transform');
            var x = transform.split(' ')[4];
            var y = transform.split(' ')[5].replace(')', '');
            var order = parent.paper.text(x, y, text);
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
