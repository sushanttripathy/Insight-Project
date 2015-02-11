/**
 * Created by Sushant on 9/27/2014.
 */
var ovrly = null;

function BeachDialog(image_id, image_url, image_cens_url, approved)
{
    this.rand_id = "dialog_"+Math.floor(Math.random()*100000);

    jQuery('#reply-div').html("<div id='"+this.rand_id+"'></div>");


    var d_div = jQuery('#'+rand_id);

    var output = "";

    var showing = 0;

    if(approved)
    {
        output += "<span>The uploaded image is shown below! No inappropriate content detected!</span>";
        output += "<div class ='displayed_image'><img src='"+image_url+"'></div>";
    }
    else
    {
        output += "<span>The uploaded image has to undergo moderation! An initial censoring of the image has been attempted (<a href='#' class='toggle_original'> Show original! </a>).</span>";
        output += "<div class ='displayed_image'><img src='"+image_cens_url+"'></div>";
        showing = 1;
    }

    d_div.append(output);

    var img_div = jQuery(d_div.find('.displayed_image'));

    jQuery(d_div.find(".toggle_original")).click(function(ev){
        if(showing)
        {
            showing = 0;
            jQuery(this).html('Show censored!');
            img_div.html("<img src='"+image_url+"'>");
        }
        else
        {
            showing = 1;
            jQuery(this).html('Show original!');
            img_div.html("<img src='"+image_cens_url+"'>");
        }
    });

    jQuery("#beach_life").qtip("toggle", true);

}

function BeachDialog2(overall_status, text_status, image_status, images_info)
{
    this.rand_id = "dialog_"+Math.floor(Math.random()*100000);

    jQuery('#reply-div').html("<div id='"+this.rand_id+"'></div>");

    var blurb_overall = '';
    var blurb_text = '';
    var blurb_images = '';

    if(overall_status == 'pos')
    {
        blurb_overall = "<div>This site seems to have unsafe content!</div>";

        text_blurb = '<div>Text : <span class="safe">safe</span></div>';
        if(text_status == 'pos')
        {
            text_blurb = '<div>Text : <span class="unsafe">unsafe</span></div>';
        }

        image_blurb = '<div>Images : <span class="safe">safe</span></div>';
        if(image_status == 'pos')
        {
            image_blurb = '<div>Images : <span class="unsafe">unsafe</span></div>';
        }

        blurb_overall += "<div>"+text_blurb+image_blurb+"</div>";


        table = "<table><tr><td>Images classes</td></tr><tr><td><div id='chart_div_res'></div></td></tr></table>";


        blurb_overall += table;

    }
    else
    {
        blurb_overall = "<div>This site does not have unsafe content!</div>";

        text_blurb = '<div>Text : <span class="safe">safe</span></div>';

        image_blurb = '<div>Images : <span class="safe">safe</span></div>';


        blurb_overall += "<div>"+text_blurb+image_blurb+"</div>";


        table = "<table><tr><td>Images classes</td></tr><tr><td><div id='chart_div_res'></div></td></tr></table>";


        blurb_overall += table;
    }

    jQuery('#'+this.rand_id).html(blurb_overall);


    var pie = new d3pie("#chart_div_res", {

        "size": {
            "canvasHeight": 400,
            "canvasWidth": 400,
            "pieInnerRadius": "44%",
            "pieOuterRadius": "64%"
        },
        "data": {
            "sortOrder": "value-desc",
            "content": [
                {
                    "label": "Safe",
                    "value": parseInt(images_info.neg),
                    "color": "#90c469"
                },
                {
                    "label": "Unsafe",
                    "value": (image_status == 'pos')?(images_info.mid_explicit):0,
                    "color": "#daca61"
                },
                {
                    "label": "Highly Unsafe",
                    "value": (image_status == 'pos')?parseInt(images_info.super_explicit):0,
                    "color": "#cb2121"
                }
            ]
        },
        "labels": {
            "outer": {
                "pieDistance": 10
            },
            "inner": {
                "hideWhenLessThanPercentage": 3
            },
            "mainLabel": {
                "fontSize": 13
            },
            "percentage": {
                "color": "#ffffff",
                "decimalPlaces": 0,
                "fontSize": 13
            },
            "value": {
                "color": "#adadad",
                "fontSize": 14
            },
            "lines": {
                "enabled": true
            }
        },
        "effects": {
            "pullOutSegmentOnClick": {
                "effect": "linear",
                "speed": 400,
                "size": 8
            }
        },
        "misc": {
            "gradient": {
                "enabled": true,
                "percentage": 100
            }
        }
    });

    jQuery("#beach_life").qtip("toggle", true);
}

jQuery(document).ready(function(){
    /*
    jQuery(window).resize(function () {
        vp_height = jQuery(window).height();
        main_text_height = vp_height - 161;
        if (main_text_height > 300)
            jQuery(".text_row").css("height", main_text_height+"px")
    });
     vp_height = jQuery(window).height();
     main_text_height = vp_height - 161;
     if (main_text_height > 300)
     jQuery(".text_row").css("height", main_text_height+"px")
    */
    jQuery("#click_change").click(function(ev){
        var is_demo_showing = jQuery("#demo_div").is(":visible");
        if(is_demo_showing)
        {
            //hide the demo div
            jQuery("#demo_div").hide(100);
            jQuery("#beach_life").show(200);

            jQuery("#current_blurb").html("Showing you image upload and URL submission forms.");
            jQuery("#click_change").html("Click here to see a random demo.");
        }
        else
        {
            jQuery("#beach_life").hide(100);
            jQuery("#demo_div").show(200);

            jQuery("#current_blurb").html("Showing you a random demo.");
            jQuery("#click_change").html("Click here to upload images or submit URLs.");
            jQuery("#beach_life").qtip("toggle", false);
        }
        ev.preventDefault();
    });

    ovrly = new Overlay(jQuery("body"), false, LOADER_32x32);

    jQuery('#beach_life').qtip({
        content:{text:"<div id='reply-div'></div>"},
        prerender: true,
        show:false,
        hide:false,
        position: {
            my: 'top left', // Use the corner...
            at: 'top right' // ...and opposite corner
        },
        style: {
            classes: 'ui-tooltip-shadow ui-tooltip-light qtip-default qtip-light qtip'
        }
    });



    jQuery('#beach_life').find(".upload_div").data("onUploadSuccess", function(file, resp_json){
        if(typeof resp_json.upload_script_response != "undefined")
        {
            if(typeof resp_json.upload_script_response.job_id != "undefined" && typeof resp_json.upload_script_response.job_ts != "undefined" && typeof resp_json.upload_script_response.job_code != "undefined")
            {
                ovrly.show_overlay(true);
                var job_id = resp_json.upload_script_response.job_id;
                var job_ts = resp_json.upload_script_response.job_ts;
                var job_code = resp_json.upload_script_response.job_code;

                AjaxPoll("jobs/getresult.php", {'job_id': job_id, 'job_ts': job_ts, 'job_code':job_code}, 6000, 100, function(resp_data){
                    var resp = jQuery.parseJSON(resp_data.responseText);
                    if(typeof resp != "undefined" && typeof resp.code != "undefined" && typeof resp.done != "undefined")
                    {
                        if(resp.done)
                        {
                            return true;
                        }
                    }
                    return false;
                }, function(resp_data){
                    ovrly.show_overlay(false);
                    var resp = jQuery.parseJSON(resp_data.responseText);

                    if(typeof resp.result != "undefined")
                    {
                        var image_id;
                        var approved = true;
                        var image_url;
                        var image_thumb_url;
                        var image_cens_url;
                        var image_cens_thumb_url;



                        if(typeof resp.result.result.id != "undefined")
                        {
                            image_id =  resp.result.result.id;

                            if(typeof  resp.result.result.approved != "undefined")
                            {
                                approved = parseInt( resp.result.result.approved);
                            }

                            if(typeof  resp.result.result.image_cloud_path != "undefined")
                            {
                                image_url = "http://images.ovrvue.com/"+ resp.result.result.image_cloud_path;
                            }

                            if(typeof  resp.result.result.image_thumb_cloud_path != "undefined")
                            {
                                image_thumb_url = "http://images.ovrvue.com/"+ resp.result.result.image_thumb_cloud_path;
                            }

                            if(typeof  resp.result.result.cens_image_cloud_path != "undefined")
                            {
                                image_cens_url = "http://images.ovrvue.com/"+ resp.result.result.cens_image_cloud_path;
                            }

                            if(typeof  resp.result.result.cens_image_thumb_cloud_path != "undefined")
                            {
                                image_cens_thumb_url = "http://images.ovrvue.com/"+ resp.result.result.cens_image_thumb_cloud_path;
                            }

                            BeachDialog(image_id, image_thumb_url, image_cens_thumb_url, approved);
                        }
                    }
                }  );
            }
        }
    });
    jQuery("#submit_button").button();
    FormHandler(jQuery('#beach_life'), {'url':{
        'null_value_allowed': false,
        'min_length':10,
        'onchange':function ( jquery_input_node, input_node_current_value, InputValidator, InputValidator_callback_function){
            makecorrectURL(jquery_input_node)
        }
    }},{
        'url':{
            'label':{
                'text':"Submit an URL to a web-page!",
                'alignment':"center"
            }
        }
    }, {
        'submit_element':"#submit_button",
        'submission_url':"ajax/urlanalyse.php",
        'submit_method' : {
            'method':'GET',
            'asynchronous': true,
            'async_callback':function(FormHandler, ResponseData, FormHandler_Callback){
                //alert(ResponseData);
                var resp = jQuery.parseJSON(ResponseData);
                if(typeof resp.code != "undefined" && !resp.code)
                {
                    if(typeof resp.script_response != "undefined")
                    {
                        var job_id = resp.script_response.job_id;
                        var job_ts = resp.script_response.job_ts;
                        var job_code = resp.script_response.job_code;

                        AjaxPoll("jobs/getresult.php", {'job_id': job_id, 'job_ts': job_ts, 'job_code':job_code}, 6000, 100, function(resp_data){
                            var resp = jQuery.parseJSON(resp_data.responseText);
                            if(typeof resp != "undefined" && typeof resp.code != "undefined" && typeof resp.done != "undefined")
                            {
                                if(resp.done)
                                {
                                    return true;
                                }
                            }
                            return false;
                        }, function(resp_data) {
                            //alert(resp_data.responseText);
                            ovrly.show_overlay(false);
                            var resp = jQuery.parseJSON(resp_data.responseText);

                            if (typeof resp.result != "undefined") {
                                if (typeof resp.result.result != "undefined")
                                {
                                    var result = resp.result.result;
                                    var overall_status = result.overall;
                                    var images_status = result.images;
                                    var text_status = result.text;
                                    var images_info = result.images_info;
                                    BeachDialog2(overall_status, text_status, images_status, images_info);
                                }

                            }
                        });
                    }
                }
                else
                {
                    FormHandler_Callback(ResponseData);
                }

            }
        }
    });

    jQuery("#submit_button").click(function(){
        jQuery("#beach_life").qtip("toggle", false);
        ovrly.show_overlay(true);
    });

    jQuery("#rundemo").button().click(function(ev){
        ovrly.show_overlay(true);
        var images_list = [];
        var out_list = [];
        jQuery("#demo_images").find(".img_div").each(function(){
            var in_path = jQuery(this).find(":input[name=in_path]").val();
            var out_path = jQuery(this).find(":input[name=out_path]").val();
            var rel_out_path =jQuery(this).find(":input[name=out_rel]").val();
            //var im_obj = {'in_path':in_path, 'out_path':out_path};
            images_list.push({'in_path':in_path, 'out_path':out_path});
            out_list.push({'out_rel_path':rel_out_path});
        });

        jQuery.ajax({
            'url':'ajax/analyse_images_list.php',
            'method':'post',
            'data':{'images_list':images_list},
            'success':function(response){
                //alert(response);
                resp = jQuery.parseJSON(response);
                if(typeof resp != "undefined" && typeof resp.code != "undefined" && !resp.code)
                {
                    var job_id = resp.script_response.job_id;
                    var job_code = resp.script_response.job_code;
                    var job_ts = resp.script_response.job_ts;

                    AjaxPoll("jobs/getresult.php", {'job_id': job_id, 'job_ts': job_ts, 'job_code':job_code}, 6000, 100, function(resp_data){
                        var resp = jQuery.parseJSON(resp_data.responseText);
                        if(typeof resp != "undefined" && typeof resp.code != "undefined" && typeof resp.done != "undefined")
                        {
                            if(resp.done)
                            {
                                return true;
                            }
                        }
                        return false;
                    }, function(resp_data) {
                        //alert(resp_data.responseText);
                        ovrly.show_overlay(false);
                        var resp = jQuery.parseJSON(resp_data.responseText);
                        jQuery("#resultant_images").html("").hide();
                        if (typeof resp.result != "undefined") {
                            for( x in out_list)
                            {
                                jQuery("#resultant_images").append('<img class="demo_image" src="'+(out_list[x].out_rel_path)+'"/>');
                            }
                        }
                        jQuery("#demo_images").hide();
                        jQuery("#resultant_images").show(200);
                    });

                }
        }});
    });
});

