/**
 * Created with JetBrains PhpStorm.
 * User: Sushant
 * Date: 4/7/13
 * Time: 12:41 PM
 * To change this template use File | Settings | File Templates.
 */
function AjaxPoll(pollurl, polldata, pollinterval, pollmaxtries, pollstopfunction, pollsuccessfunction, pollfailfunction)
{
    this.pollurl = '';
    this.pollinterval = 1000;//interval in milliseconds
    this.polltries = 0;
    this.pollmaxtries = 20;
    this.polldata = {};

    this.polltimer = 0;


    this.loopfunction = function()
    {
        var th = this;

        if(this.polltries >= this.pollmaxtries)
        {
            this.ajaxfailfunction();
        }

        this.polltries++;
        jQuery.ajax({url:th.pollurl, data:th.polldata, complete: jQuery.proxy(th.ajaxsuccessfunction, th), error:jQuery.proxy(th.ajaxfailfunction, th), cache:false});

    };

    this.ajaxsuccessfunction = function(resp){

        if(this.pollstopfunction(resp) == true)
        {
            clearInterval(this.polltimer);
            this.pollsuccessfunction(resp);
        }
    };

    this.ajaxfailfunction = function(){
        clearInterval(this.polltimer);
        this.pollfailfunction();
    };

    this.pollstopfunction = function(resp){
        //General function suitable for job polls should be overridden for other uses
        if(!resp.code)
        {
            if(resp.result && resp.result.done)
            {
                return true;
            }
        }

        return false;
    };

    this.pollsuccessfunction = function(resp)
    {

    };

    this.pollfailfunction = function()
    {

    };

    this.setup = function(pollurl, polldata, pollinterval, pollmaxtries, pollstopfunction, pollsuccessfunction, pollfailfunction)
    {
        if(typeof pollurl == "string")
        {
            this.pollurl = pollurl;

            if(typeof polldata != undefined)
                this.polldata = polldata;

            if(typeof pollinterval == "number")
                this.pollinterval = pollinterval;

            if(typeof pollmaxtries == "number")
                this.pollmaxtries = pollmaxtries;

            if(typeof pollstopfunction == "function")
                this.pollstopfunction = jQuery.proxy(pollstopfunction, this);

            if(typeof pollsuccessfunction == "function")
                this.pollsuccessfunction=jQuery.proxy(pollsuccessfunction, this);

            if(typeof pollfailfunction == "function")
                this.pollfailfunction = jQuery.proxy(pollfailfunction, this);

            var th = this;

            this.polltries = 0;

            this.polltimer = setInterval(jQuery.proxy(th.loopfunction, th), th.pollinterval);
        }
    };

    this.setup(pollurl, polldata, pollinterval, pollmaxtries, pollstopfunction, pollsuccessfunction, pollfailfunction);
}