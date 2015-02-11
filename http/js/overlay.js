/**
 * Created by Sushant on 7/19/14.
 */


var LOADER_32x32 = 'images/loading_32x32.gif';

function Overlay(target_node_or_id, show_overlay, image) {
    this.rand = Math.floor(Math.random() * 1000000);
    this.overlay_node = null;
    this.node = null;
    this.visible = false;

    this.default_image = LOADER_32x32;

    this.show_overlay = function(bool_show, image, html) {

        if(typeof image == "string" && image.length > 1)
        {
            this.overlay_node.html('<table class="overlay_table"><tr class="overlay_tr"><td class="overlay_td"><img class = "overlay_img" src="'
                + image + '"/></td></tr></table>');
        }
        else
        {
            image = this.default_image;
            this.overlay_node.html('<table class="overlay_table"><tr class="overlay_tr"><td class="overlay_td"><img class = "overlay_img" src="'
                + image + '"/></td></tr></table>');
        }

        if(typeof html == "string" && html.length > 1)
        {
            this.overlay_node.html('<table class="overlay_table"><tr class="overlay_tr"><td class="overlay_td">'+html+'</td></tr></table>');
        }

        if (typeof bool_show != "undefined" && !bool_show) {
            // hide overlay
            this.visible = false;
            this.overlay_node.hide();
        } else {
            // show overlay
            this.visible = true;
            var offs = this.node.offset();
            var ht = this.node.outerHeight();
            var wd = this.node.outerWidth();

            var z = this.node.css('z-index');

            z = parseInt(z);
            if(isNaN(z))
            {
                z = 1000;
            }
            else
            {
                z = z+1;
            }

            this.overlay_node.css('position', 'absolute').height(ht).width(wd)
                .css('top', offs.top + 'px').css('left', offs.left + 'px').css('z-index', z);// offset(offs);
            this.overlay_node.show();
        }
    };

    this.setup = function(target_node_or_id, show_overlay, image) {
        var output = '<div class="overlay_div" id="odiv_' + this.rand
            + '"> </div>';

        if (typeof target_node_or_id != "undefined") {
            if (typeof target_node_or_id == "string") {
                this.node = jQuery("#" + target_node_or_id);
            } else {
                this.node = target_node_or_id;
            }

            jQuery(document.body).append(output);

            this.overlay_node = jQuery("#odiv_" + this.rand);

            if (typeof image == "string") {
                this.overlay_node
                    .html('<table class="overlay_table"><tr class="overlay_tr"><td class="overlay_td"><img class = "overlay_img" src="'
                        + image + '"/></td></tr></table>');
            }

            if (typeof show_overlay != "undefined" && show_overlay) {
                this.show_overlay(true);
            } else {
                this.show_overlay(false);
            }
        }

    };

    this.setup(target_node_or_id, show_overlay, image);
}