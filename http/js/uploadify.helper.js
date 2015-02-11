/**
 * Created by Sushant on 9/25/2014.
 */

jQuery(document).ready(function(){
    jQuery("body").find(".upload_div").each(function(){
        var upload_div = jQuery(this);
        var upload_button = jQuery(upload_div.find("input[name='file_upload']"));

        var upload_ts = jQuery(upload_div.find("input[name='ts']")).val();
        var upload_code = jQuery(upload_div.find("input[name='code']")).val();
        var upload_allowed_extensions =  jQuery(upload_div.find("input[name='allowed_extensions']")).val();
        var upload_max_size =  parseInt(jQuery(upload_div.find("input[name='max_size']")).val());
        var upload_text = jQuery(upload_div.find("input[name='upload_text']")).val();

        if(isNaN(upload_max_size))
            upload_max_size = 0;

        var id = parseInt(upload_button.attr('id'));

        if(isNaN(id))
            id = 0;

        var upload_data = {
            'swf'      : 'flash/uploadify.swf',
            'uploader' : 'upload_scripts/uploadify.php',
            'formData' : {'id': id,  'ts':upload_ts, 'code':upload_code},
            //'debug'    : true,
            'method'   : 'post',
            'successTimeout': 300,
            'checkExisting': 'upload_scripts/check-exists.php',
            'buttonText' : upload_text,
            'onUploadError' : function(file, errorCode, errorMsg, errorString) {
                alert('The file ' + file.name + ' could not be uploaded: ' + errorString);
            },
            'onUploadSuccess' : function(file, data, response) {
                //console.log(data);
                //console.log(response);
                try
                {
                    var json_resp = jQuery.parseJSON(data);

                    if(typeof json_resp == "undefined" || typeof json_resp.code == "undefined" || json_resp.code)
                    {
                        var err_msg = "Error uploading : " + file['name'];
                        alert(err_msg);
                        return;
                    }
                    else
                    {
                        var fu = upload_div.data("onUploadSuccess");
                        if(typeof fu == "function")
                        {
                            fu(file, json_resp);
                        }
                    }
                }
                catch(err)
                {
                    alert("Error uploading : "+file);
                    return;
                }
            }
        };

        if(upload_allowed_extensions)
        {
            upload_data['fileTypeExts'] = upload_allowed_extensions;
        }

        if(upload_max_size)
        {
            upload_data['fileSizeLimit']  =  upload_max_size+'KB';
        }

        upload_button.uploadify(upload_data);
    });
});