if (!jQuery.browser.mobile) {
    jQuery('body').on('click', 'a[href^="tel:"]', function() {
            jQuery(this).attr('href', 
                jQuery(this).attr('href').replace(/^tel:/, 'callto:'));
    });
}
