<?php

ini_set('display_errors', '0');     # don't show any errors...
ini_set('max_execution_time', 120);
error_reporting(E_ALL & ~E_WARNING & ~E_NOTICE & ~E_STRICT);

include_once __DIR__ . "/../../includes/cloud_files/sclouduploadui.php";

$id = GetPost::getVar('id') + 0;


if(!empty($_FILES) && !$_FILES['Filedata']['error'] && SCloudUploadUI::validate_upload_token())
{
    $SC = new SCloudUploadUI($id);

    $json_resp_arr = array();
    $json_resp_arr['code'] = -1;

    if($SC->process_upload()) {
        $json_resp_arr['code'] = 0;
        $json_resp_arr['uploaded_cloud_path'] = $_GET['uploaded_cloud_path'];
        $json_resp_arr['uploader_id'] = $_GET['uploader_id'];

        if(isset($_GET['upload_script_response']))
            $json_resp_arr['upload_script_response'] = $_GET['upload_script_response'];

        echo json_encode($json_resp_arr);
    }
    else
    {
        echo json_encode($json_resp_arr);
    }
}
else {
    die("Error in uploaded file!");
}

