<!DOCTYPE html>
<html>
<head lang="en">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Welcome to Ovrvue!</title>
    <link type="text/css" rel="stylesheet" href="css/reset.css">
    <link type="text/css" rel="stylesheet" href="css/form.handler.css">
    <link type="text/css" rel="stylesheet" href="css/main.css">
    <link rel="stylesheet" type="text/css" href="css/uploadify.css">
    <link rel="stylesheet" type="text/css" href="css/jquery-ui.css">
    <link rel="stylesheet" type="text/css" href="css/jquery.qtip.min.css">
    <link rel="stylesheet" type="text/css" href="css/overlay.css">

    <script src="js/jquery-1.11.1.min.js" type="text/javascript"></script>
    <script src="js/jquery-ui.js" type="text/javascript"></script>
    <script src="js/jquery.uploadify.js" type="text/javascript"></script>
    <script src="js/uploadify.helper.js" type="text/javascript"></script>
    <script src="js/ajaxpoll.js" type="text/javascript"></script>
    <script src="js/overlay.js" type="text/javascript"></script>
    <script src="js/correct.js" type="text/javascript"></script>
    <script src="js/form.handler.js" type="text/javascript"></script>
    <script src="js/jquery.qtip.min.js" type="text/javascript"></script>
    <script src="js/beach.js" type="text/javascript"></script>
    <script type="text/javascript" src="js/d3.min.js"></script>
    <script type="text/javascript" src="js/d3pie.min.js"></script>
</head>
<body>
<table class="main_table">
    <tr>
        <td>
            <div class="top_header">
                <div class="logo">
                    <img src="images/logo.png">
                </div>
                <div class="top_menu">
                    <ul>
                        <li></li>
                    </ul>
                </div>
            </div>
        </td>
    </tr>
    <tr>
        <td>
            <div class="text_row">

                <!--<div class="note_div">
                    See the power of computer vision in action! Click below to check out a demo, entitled "Life's a beach"!
                </div>-->
                <div id="current_view">
                    <div id="current_blurb">Showing you image upload and URL submission forms. </div>
                    <div id="change_link_div"><a href="#" id="click_change">Click here to see a random demo.</a></div>
                </div>
                <div id="beach_life" class="note_div">
                    <table>
                        <tbody>
                        <tr>
                            <td>
                                <div class="url_input">
                                    <input type="text" name="url"/>
                                    <input type="button" name="submit" value="Submit" id="submit_button"/>
                                </div>
                            </td>
                            <td>or</td>
                            <td>
                                <?php

                                include_once __DIR__ . "/../includes/cloud_files/sclouduploadui.php";
                                date_default_timezone_set('America/Chicago');
                                $sc = new SCloudUploadUI(null, 'ovrvue_uploads', "Upload images!", array('jpg', 'jpeg', 'png'), 5120, __DIR__ . "/../includes/site_specific/process_images.php");
                                echo $sc->get_upload_div();

                                ?>

                            </td>
                        </tr>
                        </tbody>
                    </table>

                    <!--<input id="file_upload" name="file_upload" type="file" multiple="true">-->
                </div>
                <div id="demo_div">
                    <table>
                        <tr>
                            <td>
                                <div id="demo_images">
                                    <?php
                                    include_once(__DIR__ . "/../includes/site_specific/rand_pick_images.php");
                                    $root_dir = __DIR__ . "/test_images";

                                    $pos_dir = $root_dir . DIRECTORY_SEPARATOR . "pos";
                                    $neg_dir = $root_dir . DIRECTORY_SEPARATOR . "neg";

                                    $pick = SelectSamples($pos_dir, $neg_dir, 1);

                                    foreach ($pick['pos'] as $index => $value) {
                                        $rel_out_path = "out_images/".substr(md5(rand(0, 10000)), 0, 5).basename($value);
                                        $new_path = __DIR__.DIRECTORY_SEPARATOR.$rel_out_path;
                                        echo '<div class ="img_div" id="img_' . $index . '">';
                                        echo '<img class ="demo_image" src="' . "test_images/pos/".$pick['rel_pos'][$index]. '"/>';
                                        echo '<input type="hidden" name="in_path" value="'.$value.'"/>';
                                        echo '<input type="hidden" name="out_path" value="'.$new_path.'"/>';
                                        echo '<input type="hidden" name="out_rel" value="'.$rel_out_path.'" /> </div>';
                                    }

                                    foreach ($pick['neg'] as $index => $value) {
                                        $rel_out_path = "out_images/".substr(md5(rand(0, 10000)), 0, 5).basename($value);
                                        $new_path = __DIR__.DIRECTORY_SEPARATOR.$rel_out_path;
                                        echo '<div class ="img_div" id="img_' . $index . '">';
                                        echo '<img class ="demo_image" src="' . "test_images/neg/".$pick['rel_neg'][$index]. '"/>';
                                        echo '<input type="hidden" name="in_path" value="'.$value.'"/>';
                                        echo '<input type="hidden" name="out_path" value="'.$new_path.'"/>';
                                        echo '<input type="hidden" name="out_rel" value="'.$rel_out_path.'" /> </div>';
                                    }

                                    ?>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div id="resultant_images">

                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <input type="button" name="rundemo" id="rundemo" value="Run Demo"/>
                            </td>
                        </tr>
                    </table>
                </div>
                <!--<div id="reply-div"></div>-->
                <!--<script type="text/javascript" src="js/jquery-1.11.1.min.js"></script>
                <script type="text/javascript" src="js/tinymce/tinymce.min.js"></script>
                <script type="text/javascript" src="js/tinymce/jquery.tinymce.min.js"></script>

                <script type="text/javascript">
                    tinyMCE.init({
                        selector:"#editor",
                        theme: "modern"
                    });
                </script>
                <div id="editor"></div>-->
            </div>
        </td>
    </tr>
    <!--
    <tr>
        <td>
            <div class="footer_row">
                <div class="footer_row_inner">Contact us!</div>
            </div>
        </td>
    </tr>
    -->
</table>
</body>
</html>