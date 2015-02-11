<?php
/**
 * Created by PhpStorm.
 * User: Sushant
 * Date: 9/26/2014
 * Time: 4:45 AM
 */

include_once __DIR__."/../../includes/jobs/sjobs.php";
include_once __DIR__."/../../includes/getpost/getpost.php";
include_once __DIR__."/../../includes/encryption/encode.php";

$job_id = GetPost::getVar('job_id') + 0;
$job_code = GetPost::getVar('job_code');
$job_ts = GetPost::getVar('job_ts') + 0;

if(time() - $job_ts < 7200 && $job_code == Encode($job_id.'_'.$job_ts))
{
    $json_res_array = array();

    $json_res_array['code'] = 0;

    $json_res_array['done'] = false;

    $json_res_array['result'] = SJobFactory::GetJobResult($job_id);

    if($json_res_array['result'] !== null && $json_res_array['result']['result'] !== null)
    {
        $json_res_array['done'] = true;
    }

    echo json_encode($json_res_array);
}
else
{
    die();
}

