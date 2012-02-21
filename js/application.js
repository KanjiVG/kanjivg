jQuery(document).ready(function () {

    function urldecode(str) {
        return decodeURIComponent((str + '').replace(/\+/g, '%20'));
    }

    function getUrlVars() {
        var vars = [], hash;
        var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
        for (var i = 0; i < hashes.length; i++) {
            hash = hashes[i].split('=');
            vars.push(hash[0]);
            vars[hash[0]] = urldecode(hash[1]);
        }
        return vars;
    }

    function fixedFromCharCode(codePt) {
        if (codePt > 0xFFFF) {
            codePt -= 0x10000;
            return String.fromCharCode(0xD800 + (codePt >> 10), 0xDC00 + (codePt & 0x3FF));
        }
        else {
            return String.fromCharCode(codePt);
        }
    }

    var kanji = getUrlVars()["kanji"];
    if (kanji == null) {
        kanji = jQuery('#kanji').val();
    } else {
        jQuery('#kanji').val(kanji);
    }

    jQuery("#load-kanji-listing").click(function () {
        var btn = $(this);
        btn.button('loading');
        jQuery.getJSON("https://api.github.com/repos/gnurou/kanjivg/git/refs/heads/master?callback=?", function (refs) {
            var sha = refs.data.object.sha;
            jQuery.getJSON("https://api.github.com/repos/Gnurou/kanjivg/git/trees/" + sha + "?callback=?", function (results) {
                var trees = results.data.tree;
                $.each(trees, function (i, value) {
                    if (value.path == "kanji") {
                        jQuery.getJSON(value.url + "?callback=?", function (results) {
                            var trees = results.data.tree;
                            var entries = [];
                            var len = trees.length;
                            for (i = 0; i < len; i++) {
                                var value = trees[i];
                                var unicode = value.path;
                                unicode = unicode.split('.');
                                unicode = unicode[0];
                                unicode = "0x" + unicode;
                                unicode = fixedFromCharCode(unicode);
                                entries.push(' <a href="viewer.html?kanji=' + unicode + '">' + unicode + '</a> ');
                            }
                            $("#kanji-listing").append(entries.join(''));
                            btn.button('reset');
                        });
                    }
                });
            });
        })
    });

    KanjiViewer.initialize(
            "kanjiViewer",
            jQuery('#strokeWidth').val(),
            jQuery('#fontSize').val(),
            jQuery('#zoomFactor').val(),
            jQuery('#displayOrders:checked').val(),
            jQuery('#colorGroups:checked').val(),
            kanji
    );
    jQuery('#kanjiViewerParams').submit(function () {
        KanjiViewer.setFontSize(jQuery('#fontSize').val());
        KanjiViewer.setZoom(jQuery('#zoomFactor').val());
        KanjiViewer.setStrokeWidth(jQuery('#strokeWidth').val());
        KanjiViewer.setStrokeOrdersVisible(jQuery('#displayOrders:checked').val());
        KanjiViewer.setColorGroups(jQuery('#colorGroups:checked').val());
        KanjiViewer.setKanji(jQuery('#kanji').val());
        KanjiViewer.draw();
        return false;
    });
});