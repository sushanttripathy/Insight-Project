<?php
/**
 * Created by PhpStorm.
 * User: Sushant
 * Date: 1/27/2015
 * Time: 5:16 PM
 */

include_once __DIR__. "/../../includes/mongodb/smongoshards.php";
include_once __DIR__."/../../includes/jobs/sjobs.php";
include_once __DIR__."/../../includes/encryption/encode.php";

$job_id = SJobFactory::AddJob('ovrvue_urlproc', array(
    'url' => $_GET['url']
));

$job_ts = time();

$job_code = Encode($job_id.'_'.$job_ts);

$json_resp_arr = array();
$json_resp_arr['code'] = 0;
$json_resp_arr['script_response'] = array('job_id' => $job_id, 'job_ts' => $job_ts, 'job_code' => $job_code);
echo json_encode($json_resp_arr);
