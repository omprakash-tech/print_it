<?php

if (!defined('ABSPATH')) exit;

class WCDPC_Main {
    public function __construct() {
        add_action('add_meta_boxes', [$this, 'add_meta_box']);
        add_action('save_post', [$this, 'save_meta_box']);
        add_action('woocommerce_before_add_to_cart_button', [$this, 'render_dropdowns']);
        add_action('wp_enqueue_scripts', [$this, 'enqueue_scripts']);
        add_action('wp_ajax_wcdpc_get_price', [$this, 'ajax_get_price']);
        add_action('wp_ajax_nopriv_wcdpc_get_price', [$this, 'ajax_get_price']);
        add_filter('woocommerce_add_cart_item_data', [$this, 'add_cart_item_data'], 10, 3);
        add_filter('woocommerce_get_item_data', [$this, 'display_cart_meta'], 10, 2);
        add_action('woocommerce_checkout_create_order_line_item', [$this, 'add_order_item_meta'], 10, 4);
        add_filter('woocommerce_product_get_price', [$this, 'override_price'], 10, 2);
        add_filter('woocommerce_product_get_regular_price', [$this, 'override_price'], 10, 2);
    }

    public function add_meta_box() {
        add_meta_box('wcdpc_meta', 'Dynamic Pricing Options', [$this, 'render_meta_box'], 'product', 'normal', 'high');
    }

    public function render_meta_box($post) {
        $dropdowns = get_post_meta($post->ID, '_wcdpc_dropdowns', true);
        $rules = get_post_meta($post->ID, '_wcdpc_rules', true);
        wp_nonce_field('wcdpc_save_meta', 'wcdpc_nonce');
        echo '<p><label>Dropdown Names (comma separated):</label><br>';
        echo '<input type="text" name="wcdpc_dropdowns" value="' . esc_attr($dropdowns) . '" style="width:100%;"/></p>';
        echo '<p><label>Pricing Rules (one per line):</label><br>';
        echo '<textarea name="wcdpc_rules" rows="10" style="width:100%;">' . esc_textarea($rules) . '</textarea></p>';
    }

    public function save_meta_box($post_id) {
        if (!isset($_POST['wcdpc_nonce']) || !wp_verify_nonce($_POST['wcdpc_nonce'], 'wcdpc_save_meta')) return;
        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;
        if (!current_user_can('edit_post', $post_id)) return;

        update_post_meta($post_id, '_wcdpc_dropdowns', sanitize_text_field($_POST['wcdpc_dropdowns']));
        update_post_meta($post_id, '_wcdpc_rules', sanitize_textarea_field($_POST['wcdpc_rules']));
    }

    public function render_dropdowns() {
        global $product;
        $dropdowns = get_post_meta($product->get_id(), '_wcdpc_dropdowns', true);
        if (!$dropdowns) return;

        $fields = array_map('trim', explode(',', $dropdowns));
        echo '<div id="wcdpc-wrapper">';
        foreach ($fields as $field) {
            echo '<p><label>' . esc_html($field) . '</label><br>';
            echo '<select class="wcdpc-field" name="' . esc_attr($field) . '" data-name="' . esc_attr($field) . '">';
            echo '<option value="">Select ' . esc_html($field) . '</option>';
            echo '<option value="Red">Red</option><option value="Blue">Blue</option><option value="Large">Large</option><option value="Medium">Medium</option>';
            echo '</select></p>';
        }
        echo '<p><strong>Updated Price: <span id="wcdpc-price">' . wc_price($product->get_price()) . '</span></strong></p>';
        echo '</div>';
    }

    public function enqueue_scripts() {
        wp_enqueue_script('wcdpc-script', plugins_url('../assets/script.js', __FILE__), ['jquery'], null, true);
        wp_localize_script('wcdpc-script', 'wcdpc_ajax', ['url' => admin_url('admin-ajax.php')]);
    }

    public function ajax_get_price() {
        $product_id = intval($_POST['product_id']);
        $selections = $_POST['selections'];
        $rules = get_post_meta($product_id, '_wcdpc_rules', true);
        $price = null;

        foreach (explode("
", $rules) as $line) {
            list($conditions, $rule_price) = array_map('trim', explode('=>', $line));
            $pairs = array_map('trim', explode(',', $conditions));
            $match = true;
            foreach ($pairs as $pair) {
                list($key, $val) = array_map('trim', explode('=', $pair));
                if (!isset($selections[$key]) || $selections[$key] !== $val) {
                    $match = false;
                    break;
                }
            }
            if ($match) {
                $price = floatval($rule_price);
                break;
            }
        }

        echo json_encode(['price' => $price]);
        wp_die();
    }

    public function add_cart_item_data($cart_item_data, $product_id, $variation_id) {
        foreach ($_POST as $key => $value) {
            if (strpos($key, 'wcdpc_') === 0) {
                $cart_item_data[$key] = sanitize_text_field($value);
            }
        }
        return $cart_item_data;
    }

    public function display_cart_meta($item_data, $cart_item) {
        foreach ($cart_item as $key => $value) {
            if (strpos($key, 'wcdpc_') === 0) {
                $item_data[] = ['name' => ucwords(str_replace('wcdpc_', '', $key)), 'value' => $value];
            }
        }
        return $item_data;
    }

    public function add_order_item_meta($item, $cart_item_key, $values, $order) {
        foreach ($values as $key => $value) {
            if (strpos($key, 'wcdpc_') === 0) {
                $item->add_meta_data(ucwords(str_replace('wcdpc_', '', $key)), $value, true);
            }
        }
    }

    public function override_price($price, $product) {
        if (is_admin() || !is_product()) return $price;
        return $price;
    }
}
