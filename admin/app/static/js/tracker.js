function setCookie(name,value){
	var exp = new Date();
	exp.setTime(exp.getTime() + 1*60*60*1000*24*30*12);
	document.cookie = name + "="+ escape (value) + ";path=/;expires=" + exp.toGMTString();
}
function setCookie(name,value,days,domain){
	var exp = new Date();
	exp.setTime(exp.getTime() + days*24*60*60*1000);
	document.cookie = name + "="+ escape (value) + ";path=/;expires=" + exp.toGMTString() + ";domain=" + domain;
}
function getQueryString(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]); return null;
}
function getCookie(name) {
    var arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");
    if(arr=document.cookie.match(reg))
        return unescape(arr[2]); 
    else 
        return null; 
}
function trackClick(data){
    try{
        if("undefined" != typeof data){
            writelog(data,"clickview");
        }else{
            writelog(null,"clickview");
        }
    }catch(e){}
}
function trackPageview(data){
    try{
        if("undefined" != typeof data){
           writelog(data,"pageview");
        }else{
           writelog(null,"pageview");
        }
    }catch(e){}
}
function sendTrackerLog(a){(new Image).src=a}
function writelog(data,logtype){
    var cookie_days = 730;
    var url = document.URL;
    var cookie_domain = "." + url.replace(/http:\/\/.*?([^\.]+\.(com\.cn|org\.cn|net\.cn|[^\.\/]+))\/.+/, "$1");
    var log_url = "/tj.gif?r="+Math.random()+"&logv=1.0&type=" + logtype;
    var bi_hmsr ="none";
	if(getQueryString("hmsr")!=null&&getQueryString("hmsr")!=""){
        bi_hmsr = getQueryString("hmsr");
        setCookie("bi_hmsr",bi_hmsr,cookie_days,cookie_domain);
    }else{
        if(getCookie("bi_hmsr")!=null&&getCookie("bi_hmsr")!=""){
            bi_hmsr = getCookie("bi_hmsr");
        }else{
            setCookie("bi_hmsr",bi_hmsr,cookie_days,cookie_domain);
        }
    }
    var bi_hmmd ="none";
	if(getQueryString("hmmd")!=null&&getQueryString("hmmd")!=""){
        bi_hmmd = getQueryString("hmmd");
        setCookie("bi_hmmd",bi_hmmd,cookie_days,cookie_domain);
    }else{
        if(getCookie("bi_hmmd")!=null&&getCookie("bi_hmmd")!=""){
            bi_hmmd = getCookie("bi_hmmd");
        }else{
            setCookie("bi_hmmd",bi_hmmd,cookie_days,cookie_domain);
        }
    }
    var bi_hmpl ="none";
	if(getQueryString("hmpl")!=null&&getQueryString("hmpl")!=""){
        bi_hmpl = getQueryString("hmpl");
        setCookie("bi_hmpl",bi_hmpl,cookie_days,cookie_domain);
    }else{
        if(getCookie("bi_hmpl")!=null&&getCookie("bi_hmpl")!=""){
            bi_hmpl = getCookie("bi_hmpl");
        }else{
            setCookie("bi_hmpl",bi_hmpl,cookie_days,cookie_domain);
        }
    }
    var bi_hmkw ="none";
	if(getQueryString("hmkw")!=null&&getQueryString("hmkw")!=""){
        bi_hmkw = getQueryString("hmkw");
        setCookie("bi_hmkw",bi_hmkw,cookie_days,cookie_domain);
    }else{
        if(getCookie("bi_hmkw")!=null&&getCookie("bi_hmkw")!=""){
            bi_hmkw = getCookie("bi_hmkw");
        }else{
            setCookie("bi_hmkw",bi_hmkw,cookie_days,cookie_domain);
        }
    }
    var bi_cookieid = getCookie("bi_cookieid");
    if(bi_cookieid==null||bi_cookieid==""){
        bi_cookieid=(new Date).valueOf()+""+parseInt(Math.random()*10000000000);
        setCookie("bi_cookieid",bi_cookieid,cookie_days,cookie_domain);
    }
    var referrer=encodeURIComponent(document.referrer);
    if(referrer==null||referrer==""){
        referrer="none";
    }
    log_url+="&hmsr="+bi_hmsr+"&referrer="+referrer+"&cookieid="+bi_cookieid +"&hmpl="+bi_hmpl +"&hmmd="+bi_hmmd+"&hmkw="+bi_hmkw;
    if(data!=null&&logtype=="pageview"){
        for(var key in data){
            var value=data[key];
            log_url += "&"+key+"=" + value;
        }
    }else if(data!=null&&logtype=="clickview"){
        log_url += "&" + data;
    }
    sendTrackerLog(log_url);
}
try{
    if(!customer_openid) customer_openid = getCookie('BILIN_OID');
    if(customer_openid) setCookie('BILIN_OID', customer_openid, 365);
    var _hmt = _hmt || [];
    if(customer_openid){
       _hmt.push(['_setCustomVar', 1, 'openid', customer_openid, 1]);
    }
    (function() {
      var hm = document.createElement("script");
      hm.src = "//hm.baidu.com/hm.js?0849fd48c551a56e68454bc912c87929";
      var s = document.getElementsByTagName("script")[0];
      s.parentNode.insertBefore(hm, s);
    })();
}catch(e){}