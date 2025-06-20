<?php
/*
Plugin Name: WooCommerce Dynamic Price Calculator
Description: Adds dynamic pricing based on dropdowns per product.
Version: 1.0
Author: Your Name
*/

if (!defined('ABSPATH')) exit;

define('WCDPC_PLUGIN_PATH', plugin_dir_path(__FILE__));

require_once WCDPC_PLUGIN_PATH . 'includes/class-wcdpc-main.php';

function wcdpc_init_plugin() {
    $plugin = new WCDPC_Main();
}
add_action('plugins_loaded', 'wcdpc_init_plugin');
