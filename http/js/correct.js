/**
 * Created by Sushant on 1/22/2015.
 */
var correct = {};

parseUri.options = {
    strictMode : false,
    key : [ "source", "protocol", "authority", "userInfo", "user", "password",
        "host", "port", "relative", "path", "directory", "file", "query",
        "anchor" ],
    q : {
        name : "queryKey",
        parser : /(?:^|&)([^&=]*)=?([^&]*)/g
    },
    parser : {
        strict : /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
        loose : /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
    }
};

function parseUri(str) {
    var o = parseUri.options, m = o.parser[o.strictMode ? "strict" : "loose"]
        .exec(str), uri = {}, i = 14;

    while (i--)
        uri[o.key[i]] = m[i] || "";

    uri[o.q.name] = {};
    uri[o.key[12]].replace(o.q.parser, function($0, $1, $2) {
        if ($1)
            uri[o.q.name][$1] = $2;
    });

    return uri;
};

function makecorrectURL(node) {
    var retobj = {};
    retobj.success = false;
    retobj.message = '';
    retobj.showmessage = false;

    nodeval = node.val();
    if (!nodeval || typeof nodeval == 'undefined' || nodeval == '') {
        return retobj;
    }
    var arr = new Array('.com', '.net', '.org', '.biz', '.coop', '.info',
        '.museum', '.name', '.asia', '.pro', '.edu', '.gov', '.int',
        '.mil', '.ac', '.ad', '.ae', '.af', '.ag', '.ai', '.al', '.am',
        '.an', '.ao', '.aq', '.ar', '.as', '.at', '.au', '.aw', '.az',
        '.ba', '.bb', '.bd', '.be', '.bf', '.bg', '.bh', '.bi', '.bj',
        '.bm', '.bn', '.bo', '.br', '.bs', '.bt', '.bv', '.bw', '.by',
        '.bz', '.ca', '.cc', '.cd', '.cf', '.cg', '.ch', '.ci', '.ck',
        '.cl', '.cm', '.cn', '.co', '.cr', '.cu', '.cv', '.cx', '.cy',
        '.cz', '.de', '.dj', '.dk', '.dm', '.do', '.dz', '.ec', '.ee',
        '.eg', '.eh', '.er', '.es', '.et', '.fi', '.fj', '.fk', '.fm',
        '.fo', '.fr', '.ga', '.gd', '.ge', '.gf', '.gg', '.gh', '.gi',
        '.gl', '.gm', '.gn', '.gp', '.gq', '.gr', '.gs', '.gt', '.gu',
        '.gv', '.gy', '.hk', '.hm', '.hn', '.hr', '.ht', '.hu', '.id',
        '.ie', '.il', '.im', '.in', '.io', '.iq', '.ir', '.is', '.it',
        '.je', '.jm', '.jo', '.jp', '.ke', '.kg', '.kh', '.ki', '.km',
        '.kn', '.kp', '.kr', '.kw', '.ky', '.kz', '.la', '.lb', '.lc',
        '.li', '.lk', '.lr', '.ls', '.lt', '.lu', '.lv', '.ly', '.ma',
        '.mc', '.md', '.mg', '.mh', '.mk', '.ml', '.mm', '.mn', '.mo',
        '.mp', '.mq', '.mr', '.ms', '.mt', '.mu', '.mv', '.mw', '.mx',
        '.my', '.mz', '.na', '.nc', '.ne', '.nf', '.ng', '.ni', '.nl',
        '.no', '.np', '.nr', '.nu', '.nz', '.om', '.pa', '.pe', '.pf',
        '.pg', '.ph', '.pk', '.pl', '.pm', '.pn', '.pr', '.ps', '.pt',
        '.pw', '.py', '.qa', '.re', '.ro', '.rw', '.ru', '.sa', '.sb',
        '.sc', '.sd', '.se', '.sg', '.sh', '.si', '.sj', '.sk', '.sl',
        '.sm', '.sn', '.so', '.sr', '.st', '.sv', '.sy', '.sz', '.tc',
        '.td', '.tf', '.tg', '.th', '.tj', '.tk', '.tm', '.tn', '.to',
        '.tp', '.tr', '.tt', '.tv', '.tw', '.tz', '.ua', '.ug', '.uk',
        '.um', '.us', '.uy', '.uz', '.va', '.vc', '.ve', '.vg', '.vi',
        '.vn', '.vu', '.ws', '.wf', '.ye', '.yt', '.yu', '.za', '.zm',
        '.zw');
    var val = true;
    var Obj = parseUri(nodeval);
    var FinURL = '';
    if (Obj.protocol == '')
        FinURL = 'http://';
    else
        FinURL = Obj.protocol + '://';
    if (Obj.host) {
        var dot = Obj.host.lastIndexOf(".");
        if (dot >= 0) {
            var ext = Obj.host.substring(dot, Obj.host.length);
            var dname = Obj.host.substring(0, dot);
        } else {
            var ext = null;
            var dname = Obj.host;
        }
    } else {
        var dot = -1;
        var ext = null;
        var dname = null;
        if (Obj.relative) {
            dot = Obj.relative.lastIndexOf(".");
            var slash = Obj.relative.indexOf("/");
            var lastSlash = Obj.relative.lastIndexOf("/");
            if (dot >= 0) {
                ext = Obj.relative
                    .substring(
                    dot,
                    (lastSlash < 0 || lastSlash == slash) ? Obj.relative.length
                        : lastSlash);
                if (slash < 0)
                    dname = Obj.relative.substring(0, dot);
                else
                    dname = Obj.relative.substring(slash + 1, dot);
            } else {
                ext = null;
                if (slash < 0)
                    dname = Obj.relative;
                else
                    dname = (lastSlash < 0 || lastSlash == slash) ? Obj.relative
                        .substring(slash + 1)
                        : Obj.relative.substring(slash + 1, lastSlash);
            }
        }
    }
    if (ext) {
        for ( var i = 0; i < arr.length; i++) {
            if (ext == arr[i]) {
                val = true;
                break;
            } else {
                val = false;
            }
        }
    } else {
        val = false;
    }
    if (!val) {
        if (!ext || ext.length < 2)
            FinURL += dname + '.com';
        else
            FinURL += dname + ext + '.com';
    } else {
        FinURL += dname + ext;
        // FinURL += Obj.host;
    }
    FinURL = FinURL.toLowerCase();

    if (Obj.relative && Obj.host) {
        FinURL += Obj.relative;
    } else {
        FinURL += '/';
    }
    if (!dname)
        FinURL = "";
    node.val(FinURL);
    if (!FinURL.length) {
        retobj.message = 'had an invalid entry. It was cleared!';
        retobj.showmessage = true;
        return retobj;
    } else {
        retobj.success = true;
        return retobj;
    }
}

function CorrectTags(node) {
    var retobj = {};
    retobj.success = false;
    retobj.message = '';
    retobj.showmessage = false;

    var nodeval = getValue(node);

    if (!nodeval || typeof nodeval == 'undefined' || nodeval == '') {
        return retobj;
    }

    var maxtaglength = node.attr('maxtaglength');// 20;
    var tagseparator = node.attr('tagseparator');// ',';
    var maxtagcount = node.attr('maxtagcount');

    if (typeof maxtaglength == 'undefined' || isNaN(maxtaglength)) {
        maxtaglength = 20;
    }

    if (typeof tagseparator == 'undefined' || tagseparator == '') {
        tagseparator = ',';
    }

    if (typeof maxtagcount == 'undefined' || isNaN(maxtagcount)) {
        maxtagcount = 5;
    }

    var FinStr = '';
    var count = 0;
    var Splitter = nodeval.split(/[\s,]+/);// (",");
    var j = 0;
    for ( var i = 0; i < Splitter.length; i = i + 1) {
        if (Splitter[i] && Splitter[i].length) {

            if (Splitter[i].length > maxtaglength) {
                Splitter[i] = Splitter[i].substring(0, maxtaglength);
                retobj.message = retobj.message + ' All tags must be within '
                + maxtaglength + ' characters.';
            }
            count = count + 1;
            if (FinStr == '')
                FinStr = Splitter[i].toLowerCase();
            else
                FinStr = FinStr + tagseparator + Splitter[i].toLowerCase();
        }
    }
    if (count > maxtagcount) {
        retobj.message = retobj.message + "There can be a maximum of "
        + maxtagcount + " tags.";
        Splitter3 = FinStr.split(tagseparator, maxtagcount);
        FinStr = '';
        for ( var i = 0; i < maxtagcount; i++) {
            if (FinStr == '')
                FinStr = FinStr + Splitter3[i];
            else
                FinStr = FinStr + tagseparator + Splitter3[i];
        }
    }
    Splitter4 = FinStr.split(tagseparator);
    count = Splitter4.length;
    var flag = 0;

    for (i = 0; i < count; i = i + 1) {
        if (Splitter4[i] && Splitter4[i].length) {
            for (j = i + 1; j < count; j = j + 1) {
                if (Splitter4[i] == Splitter4[j]) {
                    Splitter4[j] = null;
                    if (!flag) {
                        retobj.message = retobj.message
                        + "The tags should be different.";
                        flag = true;
                    }
                }
            }
        }
    }
    FinStr = '';
    for (i = 0; i < count; i = i + 1) {
        if (Splitter4[i] && Splitter4[i].length) {
            if (FinStr == '')
                FinStr = Splitter4[i];
            else
                FinStr = FinStr + tagseparator + Splitter4[i];
        }
    }
    node.val(FinStr);
    return retobj;
}

correct.url = makecorrectURL;
correct.tags = CorrectTags;