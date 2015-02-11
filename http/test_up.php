<?php
include_once __DIR__."/../includes/cloud_files/sclouduploadui.php";

date_default_timezone_set( 'America/Chicago' );
?>

<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Test Explicit Image Filter</title>
<script src="js/jquery-1.11.1.min.js" type="text/javascript"></script>
<script src="js/jquery.uploadify.js" type="text/javascript"></script>
<script src="js/uploadify.helper.js" type="text/javascript"></script>
<script src="js/ajaxpoll.js" type="text/javascript"></script>
<script src="js/beach.js" type="text/javascript"></script>
<link rel="stylesheet" type="text/css" href="css/uploadify.css">
<style type="text/css">
body {
	font: 13px Arial, Helvetica, Sans-serif;
}
</style>
</head>

<body>
	<h1>Explicit Image Filter Demo - Stage 1</h1>
	<div id="beach_life">
        <?php
            $sc = new SCloudUploadUI(null, 'ovrvue_uploads', "Upload images!",array('jpg', 'jpeg', 'png'), 512,
                __DIR__."/../includes/site_specific/process_images.php");
            echo $sc->get_upload_div();
        ?>
		<!--<input id="file_upload" name="file_upload" type="file" multiple="true">-->
	</div>


</body>
</html>