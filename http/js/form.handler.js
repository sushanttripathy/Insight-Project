/*
 * Requires jQuery core, jQuery UI, jQuery QTip and jQuery History
 *
 * The parameter form_node can be a jQuery node or a jQuery selector string
 *
 * The parameter validation_rules is an object which has the following structure
 * {'input_name':{
 *     null_value_allowed: true/false, //optional argument default true
 *     max_length: integer, //optional argument
 *     min_length: integer, //optional argument
 *     min_value: integer, //optional in case of numeric values
 *     max_value: integer, //optional in case of numeric values
 *     regexp: 'regular expression', //optional regular expression to match against
 *     onchange: function ( jquery_input_node, input_node_current_value, InputValidator, InputValidator_callback_function){
 *         return 1;//for continued onchange event propagation
 *         return 0;//to stop further onchange event propagation
 *         return -1; // upon this return value InputValidator assumes that the function will issue a callback after it's
 *                       done processing
 *     }, //the onchange parameter is also optional the FormHandler validates the input values onchange by default
 *     validate_func: function(node, value, InputValidator, InputValidator_callback_function){
 *         return 0;//InputValidator validation is discontinued after this return value
 *         return 1;//the InputValidator object continues validation
 *         return -1;// upon this return InputValidator assumes that the function will issue a callback after it's done
 *                      processing
 *     },
 *     enable_validate: integer //possible values 0 => disable, 1 => on change, 2 => on submit, default: 1|2
 * }}
 *
 * The parameter formatting_rules is an object which has the following structure
 * {'input_name':{
 *     class: class name, //optional
 *     hovered_class: class_name, //optional
 *     focused_class: class_name, //optional
 *     label: label_text or { text:label_text, alignment: left/center/right}, //optional
 *     tooltip: tooltip_text, //optional
 *     icon:{pos: 'Apx Bpx', show:left/right}
 * }}
 *
 * The parameter submission_options is an object which has the following structure
 * {
 *  'submit_element': submit element node or jQuery selector, //required field
 *  'submission_url': url to submit to after validation, //required field
 *  'submit_method' : possible values 'GET', 'POST', {method:'GET'/'POST',
 *                                                      asynchronous: true/false, //optional parameter defaults to false
 *                                                      async_callback: function(FormHandler, ResponseData, FormHandler_Callback){},//optional and can only be specified if asynchronous is true,
 *                                                                                                      //FormHandler_Callback takes the ResponseData as argument
 *                                                      encrypted:true/false
 *                                                      }//optional parameter, default 'GET'
 * }
 *
 * #NOTES
 * The FormHandler object expects responses from the backend server in JSON format with the following structure
 * {
 *      'code':0, //0=>success
 *      'action': 0,//0=> do nothing, 1 => show info text, 2 => Hide form, 4 => Redirect to URL, 8 => Go back in history
 *      'redirect_url': url,
 *      'info_text': 'text message',
 *      'inputs_errors':
 *      {
 *          'input_name':{'message':'Any error messages', 'showMessage':true/false}
 *      }
 *
 * }
 */

function FormHandler(form_node, validation_rules, formatting_rules, submission_options)
{
    this.form_node = null;
    this.validation_rules = null;
    this.formatting_rules = null;
    this.submission_options = null;

    this.submit_node = null;

    this.continue_submit = {};

    this.timers = [];

    this.timerscount = 0;

    this.submit_via_get = function(submission_url, submit_values)
    {
        //submit via GET

        if(!!(window.history && history.pushState))
        {
            //supports HTML5 features
            jQuery.ajax(
                {
                    url:submission_url,
                    data: submit_values,
                    type: 'GET',
                    cache: false,
                    dataType:'html',
                    success: function(data) {
                        //window.history.replaceState(null, null);
                        //window.history.pushState(null, null, submission_url);
                        History.pushState(null, null, submission_url);
                        var newDoc = document.open("text/html", "replace");
                        newDoc.write(data);
                        newDoc.close();
                    }
                });
        }
        else
        {
            load_url(submission_url, submit_values, 'GET');
        }

    };

    this.submit_via_post = function(submission_url, submit_values)
    {
        //submit via POST
        if(!!(window.history && history.pushState))
        {
            //supports HTML5 features
            jQuery.ajax(
                {
                    url:submission_url,
                    data: submit_values,
                    type: 'POST',
                    cache: false,
                    dataType:'html',
                    success: function(data) {
                        //window.history.replaceState(null, null);
                        //window.history.pushState(null, null, submission_url);
                        History.pushState(null, null, submission_url);
                        var newDoc = document.open("text/html", "replace");
                        newDoc.write(data);
                        newDoc.close();
                    }
                });
        }
        else
        {
            load_url(submission_url, submit_values, 'POST');
        }
    };

    this.complex_submit = function(submission_url, submit_values, submit_method, encrypt_values, asynchronous, async_callback)
    {
        if(typeof encrypt_values != "undefined" && encrypt_values && typeof RSAPublicKey != "undefined" && typeof GLOBAL_RSAPUBLICKEY != "undefined")
        {
            //go ahead and encrypt
            var new_submit_values = {};

            var count = 0;

            for(var x in submit_values)
            {
                if(submit_values.hasOwnProperty(x))
                {
                    new_submit_values['name'+count] = encryptedString(GLOBAL_RSAPUBLICKEY, x);
                    new_submit_values['value'+count] = encryptedString(GLOBAL_RSAPUBLICKEY, submit_values[x]);
                    count++;
                }
            }
            new_submit_values['enc'] = 1;
            new_submit_values['entries'] = count;

            submit_values = new_submit_values;
        }

        if(typeof asynchronous == "undefined" || !asynchronous)
        {
            //by default asynchronous is false
            if(typeof submit_method == "undefined" || submit_method.toUpperCase() == "GET")
            {
                //default GET
                this.submit_via_get(submission_url, submit_values);
            }
            else if(submit_method.toUpperCase() == "POST")
            {
                this.submit_via_post(submission_url, submit_values);
            }
        }
        else
        {
            //Async AJAX request has to be employed
            var method = "";

            if(typeof submit_method == "undefined" || submit_method.toUpperCase() == "GET")
                method = "GET";
            else
                method = "POST";

            var th = this;

            //Showing the loading GIF overlay before submitting the AJAX request
            if(typeof this.overlay != "undefined")
            {
                this.overlay.show_overlay(true);
            }

            jQuery.ajax({
                url:submission_url,
                data: submit_values,
                type: method,
                cache: false,
                success: function(data)
                         {
                             //Hiding the overlay!
                             if(typeof th.overlay != "undefined")
                             {
                                 th.overlay.show_overlay(false);
                             }

                             if(typeof async_callback == "function")
                             {
                                async_callback(th, data, jQuery.proxy(th.process_returned_json, th));
                             }
                             else
                             {
                                 th.process_returned_json(data);
                             }
                         }
            });

        }
    };

    this.process_returned_json = function(data)
    {
        if(typeof data == "string" )
        {
            data = jQuery.parseJSON(data);
        }

        if(typeof data == "object" && data)
        {
            if(typeof data['code'] != "undefined" && data['code'])
            {
                //some error occurred
                if(typeof data['inputs_errors'] == "object" && data['inputs_errors'])
                {
                    for(x in data['inputs_errors'])
                    {
                        if(data['inputs_errors'].hasOwnProperty(x))
                        {
                            if(typeof data['inputs_errors'][x] == "object")
                            {
                                if(typeof data['inputs_errors'][x].message == "string")
                                {
                                    if(typeof data['inputs_errors'][x].showMessage != "undefined" && data['inputs_errors'][x].showMessage)
                                    {
                                        var node = jQuery(this.form_node).find(":input[name='"+x+"']");
                                        ShowErrorMessage(node, data['inputs_errors'][x].message);
                                    }
                                }
                            }
                        }
                    }
                }
            }
            else
            {
                //no error returned 'code' == 0
                if(typeof data['action'] != "undefined" && data['action'])
                {
                    if((data['action'] & 1 )&&typeof data['info_text'] == "string")
                    {
                        ShowMessage(this.form_node, data['info_text']);
                    }

                    if(data['action'] & 2)
                    {
                        jQuery(this.form_node).hide(200);
                    }

                    if((data['action'] & 4) && typeof data['redirect_url'] == "string")
                    {
                        window.location = data['redirect_url'];
                    }

                    if(data['action'] & 8)
                    {
                        History.go(-1);
                    }
                }
            }
        }
    };

    this.submit = function( timer_number)
    {
        //check if all the inputs have been validated and are ready for submission

        for(x in this.continue_submit)
        {
            if(this.continue_submit[x] == 0)
            {
                return 0; //Inputs contain some invalid values
            }
            else if(this.continue_submit[x] == -1)
            {
                //some InputValidator(s) are waiting on callback functions
                //initiate polling to check state

                if(typeof timer_number == "undefined" || timer_number === null)
                {
                    var timer_num  = this.timerscount;
                    //Setup a poll every 400 milliseconds
                    this.timers[timer_num] = window.setInterval(jQuery.proxy(this.submit, this, timer_num), 400);
                    this.timerscount++;
                }

                return -1;
            }
        }

        //All ready for submission

        //Kill the timer if it was set
        if(typeof timer_number != "undefined" && timer_number !== null)
        {
            window.clearInterval(this.timers[timer_number]);
        }

        //now moving on to submission

        if(typeof this.submission_options != "undefined" && typeof this.submission_options.submission_url == "string")
        {
            //get the submission url

            var submission_url = this.submission_options.submission_url;

            //now get the values of the validated inputs

            var submit_values = {};

            jQuery(this.form_node).find(":input").each(function(){
                var name = jQuery(this).attr('name');

                submit_values[name] = jQuery(this).val();

            });


            if(typeof this.submission_options.submit_method == "undefined")
            {
                this.submit_via_get(submission_url, submit_values);
            }
            else if(typeof this.submission_options.submit_method == "string")
            {
                //GET or POST
                if(this.submission_options.submit_method.toUpperCase() == "GET")
                {
                    this.submit_via_get(submission_url, submit_values);
                }
                else if(this.submission_options.submit_method.toUpperCase() == "POST")
                {
                    this.submit_via_post(submission_url, submit_values);
                }
            }
            else if(typeof this.submission_options.submit_method == "object")
            {
                //complicated options
                var async = null;
                var encrypt = null;
                var method = null;
                var async_callback = null;

                if(typeof this.submission_options.submit_method.method == "string")
                {
                    method = this.submission_options.submit_method.method;
                }

                if(typeof this.submission_options.submit_method.asynchronous != "undefined")
                {
                    async = this.submission_options.submit_method.asynchronous;
                }

                if(typeof this.submission_options.submit_method.encrypted != "undefined")
                {
                    encrypt = this.submission_options.submit_method.encrypted;
                }

                if(typeof this.submission_options.submit_method.async_callback == "function")
                {
                    async_callback = this.submission_options.submit_method.async_callback;
                }

                this.complex_submit(submission_url, submit_values, method, encrypt, async, async_callback);
            }
        }

    };

    this.setup = function(form_node, validation_rules, formatting_rules, submission_options)
    {
      if(typeof form_node != "undefined")
      {
          if(typeof form_node == "object" || typeof form_node == "string")
          {
              this.form_node = jQuery(form_node);
          }

          if(typeof this.form_node != "undefined")
          {
              if(typeof Overlay == "function")
              {
                  this.overlay = new Overlay(this.form_node, false);
              }
              if(typeof validation_rules == "object")
              {
                  this.validation_rules = validation_rules;
              }

              if(typeof formatting_rules == "object")
              {
                  this.formatting_rules = formatting_rules;
              }

              if(typeof submission_options == "object")
              {
                  this.submission_options = submission_options;
              }

              if(typeof this.submission_options.submit_element != "undefined")
              {
                  this.submit_node = jQuery(this.submission_options.submit_element);
              }
              else
              {
                  return null;
              }

              //now start parsing through the child elements and identify the child elements

              var th = this; //reference to this FormHandler object

              jQuery(this.form_node).find(":input").each(function(){
                  var name = jQuery(this).attr('name');

                  if(typeof th.formatting_rules != "undefined" && typeof th.formatting_rules[name] == "object")
                  {
                      var input_formatter = new InputFormatter(jQuery(this), th.formatting_rules[name], th);
                      jQuery(this).data("FormatterObject", input_formatter);
                  }
              });

              jQuery(this.form_node).find(":input").each(function(){
                  var name = jQuery(this).attr('name');

                  th.continue_submit[name] = 1;

                  if(typeof th.validation_rules != "undefined" && typeof th.validation_rules[name] == "object")
                  {
                      var input_validator = new InputValidator(jQuery(this), th.validation_rules[name], th);
                      jQuery(this).data("ValidatorObject", input_validator);
                  }
              });

              //register the submit element click function last
              this.submit_node.click(jQuery.proxy(this.submit, this));

          }
      }

    };

    this.setup(form_node, validation_rules, formatting_rules, submission_options);

}

/*
 * The parameter validation_rules is an object which has the following structure
 * {
 *     null_value_allowed: true,//optional argument
 *     max_length: integer, //optional argument
 *     min_length: integer, //optional argument
 *     min_value: float, //optional in case of numeric values
 *     max_value: float, //optional in case of numeric values
 *     regexp: 'regular expression', //optional regular expression to match against
 *     onchange: function ( jquery_input_node, input_node_current_value, InputValidator, InputValidator_callback_function){
 *         return 1;//for continued onchange event propagation
 *         return 0;//to stop further onchange event propagation
 *         return -1; // upon this return value InputValidator assumes that the function will issue a callback after it's
 *                       done processing
 *     }, //the onchange parameter is also optional the FormHandler validates the input values onchange by default
 *     validate_func: function(node, value, InputValidator, InputValidator_callback_function){
 *         return 0;//InputValidator validation is discontinued after this return value
 *         return 1;//the InputValidator object continues validation
 *         return -1;// upon this return InputValidator assumes that the function will issue a callback after it's done
 *                      processing
 *     },
 *     enable_validate: integer //possible values 0 => disable, 1 => on change, 2 => on submit, default: 1|2
 * }
 *
 */

function InputValidator(node, validation_rules, parent_obj)
{
    this.node = node;
    this.validation_rules = validation_rules;
    this.parent_object = parent_obj;
    this.message = "";

    this.notify_parent = function(submit_val)
    {
        if(typeof this.parent_object == "object")
        {
            var cur_node_name = jQuery(this.node).attr("name");

            if(typeof this.parent_object.continue_submit[cur_node_name] != "undefined")
                this.parent_object.continue_submit[cur_node_name] = submit_val;
        }
    }

    this.isValid = function()
    {
        var cur_val = jQuery(this.node).val();

        if(typeof this.validation_rules == "object" )
        {
            if(typeof this.validation_rules.max_length != "undefined")
            {
                var max_length = parseInt(this.validation_rules.max_length);

                if(!isNaN(max_length))
                {
                    if(cur_val && cur_val.length > max_length)
                    {
                        this.message = "Input value length is longer than allowed!";
                        return 0;
                    }
                }
            }

            if(typeof this.validation_rules.min_length != "undefined")
            {
                var min_length = parseInt(this.validation_rules.min_length);

                if(!isNaN(min_length))
                {
                    if(cur_val && cur_val.length < min_length)
                    {
                        this.message = "Input value length is shorter than allowed!";
                        this.notify_parent(0);
                        return 0;
                    }
                    if (typeof this.validation_rules.null_value_allowed != "undefined" && !this.validation_rules.null_value_allowed && (typeof cur_val == "undefined" ||!cur_val))
                    {
                        this.message = "Input value is required!";
                        return 0;
                    }
                }
            }

            var cur_real_val = parseFloat(cur_val);

            if(typeof this.validation_rules.max_value != "undefined")
            {
                var max_value = parseFloat(this.validation_rules.max_value);

                if(!isNaN(max_value))
                {
                    if(isNaN(cur_real_val))
                    {
                        this.message = "Input value is not a number!";
                        return 0;
                    }
                    if (cur_real_val > max_value)
                    {
                        this.message = "Input value is greater than the maximum allowed limit!";
                        return 0;
                    }
                }
            }

            if(typeof this.validation_rules.min_value != "undefined")
            {
                var min_value = parseFloat(this.validation_rules.min_value);

                if(!isNaN(min_value))
                {
                    if(isNaN(cur_real_val))
                    {
                        this.message = "Input value is not a number!";
                        return 0;
                    }
                    if (cur_real_val < min_value)
                    {
                        this.message = "Input value is lower than the minimum allowed limit!";
                        return 0;
                    }
                }
            }

            if(typeof this.validation_rules.regexp != "undefined")
            {
                var pattern = this.validation_rules.regexp;

                if(cur_val && !pattern.test(cur_val))
                {
                    this.message = "Input value is invalid!";
                    return 0;
                }
            }
        }
        return 1;
    };

    this.change_handler_callback = function(cont)
    {
        if(typeof cont == "undefined" || cont)
        {
            //now call the user defined validation function if it exists

            if(typeof this.validation_rules.validate_func == "function")
            {
                var ret_val = 0;

                ret_val = this.validation_rules.validate_func(this.node, cur_val, this, jQuery.proxy(this.validation_handler_callback, this));

                if(!ret_val || ret_val == -1)
                {
                    return ret_val;
                }
            }

            //now call the isValid function

            if(!this.isValid())
            {
                this.notify_parent(0);
                ShowErrorMessage(this.node, this.message);
                return 0;
            }

            this.notify_parent(1);
            return 1;
        }
        this.notify_parent(0);
        return 0;
    };

    this.validation_handler_callback = function(cont)
    {
        if(typeof cont == "undefined" || cont)
        {
            //now call the isValid function

            if(!this.isValid())
            {
                this.notify_parent(0);
                ShowErrorMessage(this.node, this.message);
                return 0;
            }

            this.notify_parent(1);
            return 1;
        }

        this.notify_parent(0);
        return 0;
    };

    this.validate = function(ev)
    {
        var cur_val = jQuery(this.node).val();

        if(typeof this.validation_rules == "object")
        {
            if(typeof ev != "undefined" && typeof ev.type != "undefined")
            {
                if(ev.type == "change")
                {
                    //on change validation
                    //first call the user defined onchange function if it exists


                    if(typeof this.validation_rules.onchange == "function")
                    {
                        var ret_val = 0;

                        ret_val = this.validation_rules.onchange(this.node, cur_val, this, jQuery.proxy(this.change_handler_callback, this));

                        if(!ret_val || ret_val == -1)
                        {
                            this.notify_parent(ret_val);
                            return ret_val;
                        }
                    }

                    //next call the user defined validation function if it exists

                    if(typeof this.validation_rules.validate_func == "function")
                    {
                        var ret_val = 0;

                        ret_val = this.validation_rules.validate_func(this.node, cur_val, this, jQuery.proxy(this.validation_handler_callback, this));

                        if(!ret_val || ret_val == -1)
                        {
                            this.notify_parent(ret_val);
                            return ret_val;
                        }
                    }

                    //now call the isValid function

                    if(!this.isValid())
                    {
                        this.notify_parent(0);
                        ShowErrorMessage(this.node, this.message);
                        return 0;
                    }
                }
                else if(ev.type == "click")
                {
                    //on submit validation

                    //first call the user defined validation function if it exists

                    if(typeof this.validation_rules.validate_func == "function")
                    {
                        var ret_val = 0;

                        ret_val = this.validation_rules.validate_func(this.node, cur_val, this, jQuery.proxy(this.validation_handler_callback, this));

                        if(!ret_val || ret_val == -1)
                        {
                            this.notify_parent(ret_val);
                            return ret_val;
                        }
                    }

                    //now call the isValid function

                    if(!this.isValid())
                    {
                        this.notify_parent(0);
                        ShowErrorMessage(this.node, this.message);
                        return 0;
                    }
                }
            }
        }
        this.notify_parent(1);
        return 1;
    };

    if(typeof this.validation_rules.enable_validate == "number")
    {
        if(this.validation_rules.enable_validate & 1)
        {
            //validate on change
            jQuery(this.node).change(jQuery.proxy(this.validate, this ));
        }

        if(this.validation_rules.enable_validate & 2)
        {
            //validate on submit

            if(typeof this.parent_object.submit_node != "undefined")
            {
                jQuery(this.parent_object.submit_node).click(jQuery.proxy(this.validate, this ));
            }

        }
    }
    else
    {
        //default behavior

        //validate on change
        jQuery(this.node).change(jQuery.proxy(this.validate, this ));


        //validate on submit

        if(typeof this.parent_object.submit_node != "undefined")
        {
            jQuery(this.parent_object.submit_node).click(jQuery.proxy(this.validate, this ));
        }
    }
}

function InputFormatter(node, formatting_rules, parent_obj)
{
    this.node = node;
    this.formatting_rules = formatting_rules;
    this.parent_object = parent_obj;

    this.label_node = null;
    this.input_node = null;
    this.icon_node = null;

    this.label_visible = false;

    //this.orig_classes = null;

    if(this.formatting_rules.hasOwnProperty("label") && typeof this.formatting_rules["label"] != "undefined" ||
        this.formatting_rules.hasOwnProperty("icon") && typeof this.formatting_rules["icon"] != "undefined")
    {
        var n_html = jQuery(this.node).clone().wrap('<p>').parent().html();

        var rand_divid = 'id_'+ Math.floor(Math.random()*1000000);
        var output = "<div id='"+rand_divid+"' class='input_container'></div>";

        var n_border_style = jQuery(this.node).css('border-style');

        var n_border_width_l = jQuery(this.node).css('border-left-width');
        var n_border_width_r = jQuery(this.node).css('border-right-width');
        var n_border_width_t = jQuery(this.node).css('border-top-width');
        var n_border_width_b = jQuery(this.node).css('border-bottom-width');

        var n_width = jQuery(this.node).width();
        var n_height = jQuery(this.node).height();



        jQuery(this.node).replaceWith(output);

        this.node = jQuery('#'+rand_divid);

        //jQuery(this.node).css('border-style',  n_border_style);
        //jQuery(this.node).css('border-left-width',  n_border_width_l);
        //jQuery(this.node).css('border-right-width',  n_border_width_r);
        //jQuery(this.node).css('border-top-width',  n_border_width_t);
        //jQuery(this.node).css('border-bottom-width',  n_border_width_b);

        //jQuery(this.node).css('width', n_width+'px');
        //jQuery(this.node).css('height', n_height+'px');



        jQuery(this.node).append('<div class="input_div"></div>');

        jQuery(this.node).append('<div class="label_div"></div>');

        jQuery(this.node).append('<span class="icon_span"></div>')

        this.input_node = jQuery(this.node).find(".input_div");
        this.label_node = jQuery(this.node).find(".label_div");
        this.icon_node = jQuery(this.node).find(".icon_span");

        this.input_node.html(n_html);

        if(typeof this.formatting_rules["label"] == "object")
        {
            if(typeof this.formatting_rules["label"].text == "string")
            {
                jQuery(this.label_node).html(this.formatting_rules["label"].text);
            }

            if(typeof this.formatting_rules["label"].alignment == "string")
            {
                jQuery(this.label_node).css('text-align',this.formatting_rules["label"].alignment );
            }
        }
        else if(typeof this.formatting_rules["label"] == "string")
        {
            jQuery(this.label_node).html(this.formatting_rules["label"]);
        }

        if(typeof this.formatting_rules["icon"] == "object")
        {
            jQuery(this.icon_node).css('display', 'block');
            jQuery(this.icon_node).css('width', '16px');
            jQuery(this.icon_node).css('height', '16px');

            if(typeof this.formatting_rules['icon'].pos == "string")
            {
                jQuery(this.icon_node).css("background-position", this.formatting_rules['icon'].pos);
            }

            if(typeof this.formatting_rules['icon'].show == "string" )
            {
                jQuery(this.icon_node).css('float', this.formatting_rules['icon'].show);
            }
        }

        var th = this;

        jQuery(this.node).focusin(function(){
            if(th.label_visible)
            {
                th.label_visible = false;
                jQuery(th.label_node).hide();
                //jQuery(th.input_node).show();
                //jQuery(th.icon_node).show();
                jQuery(th.input_node).find(":input").focus();
            }
        });
        jQuery(this.node).click(function(){

            if(th.label_visible)
            {
                th.label_visible = false;
                jQuery(th.label_node).hide();
                //jQuery(th.input_node).show();
                //jQuery(th.icon_node).show();
                jQuery(th.input_node).find(":input").focus();
            }

        });

        jQuery(this.node).focusout(function(){
            if(!th.label_visible)
            {
                if(jQuery(th.input_node).find(":input").val() == '')
                {
                    th.label_visible = true;
                    th.label_node.show();
                }
            }
        });

        //this.input_node.hide();
        //this.icon_node.hide();
        this.label_visible = true;

    }

    if(this.formatting_rules.hasOwnProperty("class") && typeof this.formatting_rules["class"] == "string")
    {
        jQuery(this.node).addClass(this.formatting_rules["class"]);
    }

    if(this.formatting_rules.hasOwnProperty("hovered_class") && typeof this.formatting_rules["hovered_class"] == "string")
    {
        jQuery(this.node).hover(function(){
            jQuery(th.node).addClass(th.formatting_rules["hovered_class"]);
            return true;
        }, function(){
            jQuery(th.node).removeClass(th.formatting_rules["hovered_class"]);
            return true;
        });
    }

    if(this.formatting_rules.hasOwnProperty("focused_class") && typeof this.formatting_rules["focused_class"] == "string")
    {
        jQuery(th.node).focusin(function(){
            jQuery(th.node).addClass(th.formatting_rules["focused_class"]);
            return true;
        });

        jQuery(th.node).focusout(function(){
            jQuery(th.node).removeClass(th.formatting_rules["focused_class"]);
            return true;
        });
    }

    if(this.formatting_rules.hasOwnProperty("tooltip") && typeof this.formatting_rules["tooltip"] == "string")
    {
        HoverMessage(this.node, this.formatting_rules["tooltip"]);
    }
}

function ShowErrorMessage(node, message)
{
    if(!node || !node.length)
        return;
    var isVisible = false;
    do
    {
        isVisible = node.is(":visible");
        if(!isVisible)
        {
            node = jQuery(node.parent());
        }
    }while(!isVisible);

    node.removeData('qtip')
        .qtip({
            content: {
                text: message
            },
            position: {
                my: 'left bottom', // Use the corner...
                at: 'right bottom' // ...and opposite corner
            },
            show: {
                event: false,
                ready: true
            },
            hide: 'change mouseover focus',
            style: {
                classes: 'ui-tooltip-shadow ui-tooltip-red'
            }
        });
}

function ShowMessage(node, message)
{
    if(!node|| !node.length)
        return;
    var isVisible = false;
    do
    {
        isVisible = node.is(":visible");
        if(!isVisible)
        {
            node = jQuery(node.parent());
        }
    }while(!isVisible);

    node.removeData('qtip')
        .qtip({
            content: {
                text: message
            },
            position: {
                my: 'left top', // Use the corner...
                at: 'right top' // ...and opposite corner
            },
            show: {
                event: false,
                ready: true
            },
            hide: 'change',
            style: {
                classes: 'ui-tooltip-shadow ui-tooltip-light'
            }
        });
}

function HoverMessageB(node, message)
{
    if(!node|| !node.length)
        return;
    node.removeData('qtip')
        .qtip({
            content: {
                text: message
            },
            position: {
                my: 'left bottom', // Use the corner...
                at: 'right bottom' // ...and opposite corner
            },
            show: {
                event: 'mouseover',
                ready: false
            },
            hide: 'mouseout focus',
            style: {
                classes: 'ui-tooltip-shadow ui-tooltip-light'
            }
        });
}

function HoverMessage(node, message)
{
    if(!node|| !node.length)
        return;
    var isVisible = false;
    do
    {
        isVisible = node.is(":visible");
        if(!isVisible)
        {
            node = jQuery(node.parent());
        }
    }while(!isVisible);
    node.removeData('qtip')
        .qtip({
            content: {
                text: message
            },
            position: {
                my: 'left bottom', // Use the corner...
                at: 'right bottom' // ...and opposite corner
            },
            show: {
                event: 'mouseover',
                ready: false
            },
            hide: 'mouseout focus',
            style: {
                classes: 'ui-tooltip-shadow ui-tooltip-light'
            }
        });
}

function load_url(url, data, method) {
    if(typeof method == "undefined")
        method = "GET"; //default method is GET

    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", url);

    for(var key in data) {
        if(data.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", data[key]);

            form.appendChild(hiddenField);
        }
    }

    document.body.appendChild(form);
    form.submit();
}

/*
var F = new FormHandler("#don",{
        'Okie':{
            null_value_allowed:false,
            max_length: 10,
            min_length: 5,
            min_value: '-1.1',
            max_value: '2.2',
            regexp:/^[-]?[0-9]*[.]?[0-9]+$/i,
            onchange: function (node, val, validator, callback){
                jQuery(node).val(jQuery.trim(val));
                return true;
            },
            validate_func: function(){
                return true;
            },
            enable_validate: 3
        },
        'Dokie':{
            max_length: 10,
            min_length: 5,
            min_value: '-1.1',
            max_value: '200000',
            regexp:/^[-]?[0-9]*[.]?[0-9]+$/i,
            onchange: function (){
                return true;
            },
            validate_func: function(){
                return true;
            },
            enable_validate: 3
        }
    },
    {
        'Okie':{},
        'Dokie':{}
    },
    {
        submit_element:"#von",
        submission_url:"test_submit",
        'submit_method' : {
                    method:"GET",
                    asynchronous: true,
                    async_callback: function(obj, data, callback)
                                    {
                                        callback(data);
                                    },
                    encrypted: true
        }
    }
);
*/

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}
