<?php
/*
Plugin Name: Newsletter Subscription
Description: A custom plugin to handle newsletter subscriptions.
Version: 1.0
Author: Ardijan
*/

function handle_subscription_form() {
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['subscribe_email'])) {
        $email = sanitize_email($_POST['subscribe_email']);
        
        // Save the email as needed
        // For demonstration, we'll save it as a custom post type
        $post_id = wp_insert_post(array(
            'post_title' => $email,
            'post_type' => 'subscribed_emails', // Custom post type for subscribed emails
            'post_status' => 'publish',
        ));
        
     if ($post_id) {
            // Apply the coupon code to the user's cart
            // $coupon_code = '8KGUK5P2'; // Replace with your actual coupon code
            $coupon_code = get_option('coupon_code', '');
            WC()->cart->apply_coupon($coupon_code);
            $cssStyle = '<style>#subscription-message{ display:block !important }</style>';
            setcookie('newsletter_subscribed', 'true', time() + 604800, '/'); // Cookie set for 1 week (604800 seconds)
            // Display the message in a specific HTML element with an ID
            echo $cssStyle;
        } else {
            // Handle error, if any
            echo '<p id="subscription-message">'.esc_html($subscription_message_failed).'</p>';
        }
        // Prevent WordPress from processing the request further
    }
}

add_action('init', 'handle_subscription_form');


// Add the following code to display the subscription form and popup
function display_subscription_popup() {
    // Output the HTML and CSS for the subscription form and popup
    $enabled = get_option('popup_enabled', 1);
    $custom_text_one = get_option('custom_text_one', 'Custom Text One');
    $custom_text_two = get_option('custom_text_two', 'Custom Text Two');
    $custom_text_three = get_option('custom_text_three', 'Custom Text Three');
    $custom_text_buton = get_option('custom_text_buton', 'Custom Text Button');
    if ($enabled) {
    echo '
    <style>
    .wrapper_sub {
        opacity:0;
  		transition: opacity 0.5s;
		width: 500px;
		position: fixed;
		z-index: 99999;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
		padding: 20px;
		background: url(https://dev3.digitalflow.dev/wp-content/uploads/2023/10/unnamed-5.jpg);
	}
	.inner_content_sub {
		padding: 30px;
		background: #FFFBF5;
		border-radius: 40px;
		width: 410px;
		margin: auto;
	}
	.wrapper_text {
		display:flex;
		align-items: center;
	}
	.wrapper_text img {
		width: 50%;
    	margin-left: 20px;
	}
	.wrapper_sub {
		margin:auto;
	    padding-bottom: 50px;
    	border-radius: 5px;
	}
	.form_sub {
		display:flex;
		margin-bottom: 0;
	}
	input#subscribe_email {
		width: 100%;
		border: 0.4px solid #3d3d3d2e;
		border-radius: 11px;
	}
	#submit_button {
		background: #F1D5AF;
		border-radius: 20px;
		width: 250px;
		margin-top: 20px;
		position: absolute;
		bottom: 22px;
		left: 25%;
		padding: 13px;
		color: #3D3D3D;
		font-weight: 600;
	}
	.logo_newsletter {
		margin:auto;
		padding-bottom: 20px;
	}
	.wrapper_text h1 {
		font-family: LindexSans;
		font-size: 64px;
		font-weight: 500;
		width: 50%;
	}
	.inner_content_sub p {
		color: #3D3D3D;
		width: 80%;
		text-align: center;
		font-weight: 600;
	}
	#close_popup {
		position: absolute;
		right: 10px;
		top: -20px;
		cursor: pointer;
	}
	#close_popup svg {
		width: 20px;
	}
	#subscription-message {
		display:none;
		font-size: 14px;
		text-align: center;
		margin-top: 10px;
		background: #90B1A7;
		width: max-content;
		margin-left: auto;
		margin-right: auto;
		padding: 7px;
		border-radius: 6px;
		color: white;
		font-weight: 500;
	}
    </style>
    <div class="wrapper_sub">
    <img class="logo_newsletter" src="https://dev3.digitalflow.dev/wp-content/uploads/2023/09/LindexLogo.png">
    <a id="close_popup">	
        <svg width="94" height="94" viewBox="0 0 94 94" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M47.14 89.78C70.867 89.78 90.28 70.367 90.28 46.64C90.28 22.913 70.867 3.5 47.14 3.5C23.413 3.5 4 22.913 4 46.64C4 70.367 23.413 89.78 47.14 89.78Z" stroke="black" stroke-width="6.471" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M34.9313 58.8486L59.3486 34.4316" stroke="black" stroke-width="6.471" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M59.3486 58.8486L34.9313 34.4316" stroke="black" stroke-width="6.471" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </a>
    <div class="inner_content_sub">
        <div class="wrapper_text">
        <h1>' . $custom_text_one . '</h1>
            <img src="https://dev3.digitalflow.dev/wp-content/uploads/2023/10/czM6Ly9tZWRpYS1wcml2YXRlLmNhbnZhLmNvbS81dUpyMC9NQUZ3Vkg1dUpyMC8xL3AucG5n.webp">
        </div>
        <p>' . $custom_text_two . '</p>
    <form action="" method="post" class="form_sub" id="subscription-form">
        <label style="display:none;" for="subscribe_email">Email for Subscription:</label>
        <input type="email" name="subscribe_email" id="subscribe_email" placeholder="Shkuraj Email per te abonuar" required>
        <input type="submit" value="' . $custom_text_buton . '" id="submit_button">
    </form>
    <div id="subscription-message">' . $custom_text_three . '</div>
    </div>
    </div>
    <script>
    
    document.addEventListener("DOMContentLoaded", function () {        
        const newsletterSubscribedCookie = document.cookie.replace(/(?:(?:^|.*;\s*)newsletter_subscribed\s*=\s*([^;]*).*$)|^.*$/, "$1");
        const delayTriggeredCookie = document.cookie.replace(/(?:(?:^|.*;\s*)delay_triggered\s*=\s*([^;]*).*$)|^.*$/, "$1");
    
        if (newsletterSubscribedCookie === "true" && delayTriggeredCookie !== "true") {
            // Set a timeout to hide the popup after 15 seconds
            setTimeout(function () {
                document.querySelector(".wrapper_sub").style.display = "none";
                // Set a cookie to indicate that the delay has been triggered
                document.cookie = "delay_triggered=true; max-age=2386400"; // This will expire in 24 hours
            }, 10000);
        }
        if (delayTriggeredCookie === "true") {
            document.querySelector(".wrapper_sub").style.display = "none";
        }
        document.getElementById("close_popup").addEventListener("click", function() {
            document.querySelector(".wrapper_sub").style.display = "none";
        });
    });
    document.addEventListener("DOMContentLoaded", function () {
        const hidePopupCookie = document.cookie.replace(/(?:(?:^|.*;\s*)hide_popup\s*=\s*([^;]*).*$)|^.*$/, "$1");
        
    
    
        // Close button functionality
        document.getElementById("close_popup").addEventListener("click", function() {
            // Set the hide_popup cookie to "true" with an expiration of one week (604800 seconds)
            const oneWeekInSeconds = 604800;
            const expirationDate = new Date();
            expirationDate.setTime(expirationDate.getTime() + (oneWeekInSeconds * 1000));
            document.cookie = `hide_popup=true; expires=${expirationDate.toUTCString()}; path=/`;
    
            // Hide the popup
            document.querySelector(".wrapper_sub").style.display = "none";
        });
    
        if (hidePopupCookie === "true") {
            // Show the popup since the hide_popup cookie doesn"t exist or is not set to "true"
            document.querySelector(".wrapper_sub").style.display = "none";
        }
    });
 
    window.addEventListener("load", function () {
        setTimeout(function () {
          const wrapper = document.querySelector(".wrapper_sub");
          if (wrapper) {
            wrapper.style.opacity = 1;
          }
        }, 3000); // 10000 milliseconds = 10 seconds
      });
    </script>';
}
}


add_action('wp_footer', 'display_subscription_popup');


function plugin_settings_page() {
    ?>
    <div class="wrap">
        <h2>Newsletter Subscription Settings</h2>
        <form method="post" action="options.php">
            <?php
            settings_fields('newsletter_subscription_options');
            do_settings_sections('newsletter_subscription_settings');
            submit_button();
            ?>
        </form>
    </div>
    <?php
}

function plugin_settings() {
    // Register the settings
    register_setting('newsletter_subscription_options', 'popup_enabled');
    register_setting('newsletter_subscription_options', 'popup_text');
    register_setting('newsletter_subscription_options', 'custom_text_one');
    register_setting('newsletter_subscription_options', 'custom_text_two');
    register_setting('newsletter_subscription_options', 'custom_text_three');
    register_setting('newsletter_subscription_options', 'custom_text_buton');
    register_setting('newsletter_subscription_options', 'coupon_code'); 


    // Add a section for enabling/disabling the popup
    add_settings_section('popup_settings_section', 'Popup Settings', 'popup_settings_section_callback', 'newsletter_subscription_settings');

    // Add fields for enabling/disabling the popup and customizing the text
    add_settings_field('popup_enabled', 'Enable Popup', 'popup_enabled_callback', 'newsletter_subscription_settings', 'popup_settings_section');
    add_settings_field('popup_text', 'Popup Text', 'newsletter_subscription_settings', 'popup_settings_section');
    add_settings_field('custom_text_one', 'Title Discount', 'custom_text_one_callback', 'newsletter_subscription_settings', 'popup_settings_section');
    add_settings_field('custom_text_two', 'Description', 'custom_text_two_callback', 'newsletter_subscription_settings', 'popup_settings_section');
    add_settings_field('custom_text_three', 'Succesful Message', 'custom_text_three_callback', 'newsletter_subscription_settings', 'popup_settings_section');
    add_settings_field('custom_text_buton', 'Button Text', 'custom_text_buton_callback', 'newsletter_subscription_settings', 'popup_settings_section');
    add_settings_field('coupon_code', 'Coupon Code', 'coupon_code_callback', 'newsletter_subscription_settings', 'popup_settings_section'); // Add the coupon code field

}

function popup_settings_section_callback() {
    echo 'Customize your popup settings here.';
}

function popup_enabled_callback() {
    $enabled = get_option('popup_enabled');
    echo '<input type="checkbox" name="popup_enabled" ' . checked(1, $enabled, false) . ' value="1">';
}
function custom_text_one_callback() {
    $text = get_option('custom_text_one', 'Custom Text One');
    echo '<input type="text" name="custom_text_one" value="' . esc_attr($text) . '">';
}

function custom_text_two_callback() {
    $text = get_option('custom_text_two', 'Custom Text Two');
    echo '<input type="text" name="custom_text_two" value="' . esc_attr($text) . '">';
}

function custom_text_three_callback() {
    $text = get_option('custom_text_three', 'Custom Text Three');
    echo '<input type="text" name="custom_text_three" value="' . esc_attr($text) . '">';
}

function custom_text_buton_callback() {
    $text = get_option('custom_text_buton', 'Custom Text Button');
    echo '<input type="text" name="custom_text_buton" value="' . esc_attr($text) . '">';
}
function coupon_code_callback() {
    $coupon_code = get_option('coupon_code', ''); // Retrieve the current coupon code value
    echo '<input type="text" name="coupon_code" value="' . esc_attr($coupon_code) . '">';
}
// Add the settings page to the admin menu
function add_settings_page() {
    add_submenu_page('options-general.php', 'Newsletter Subscription Settings', 'Newsletter Subscription', 'manage_options', 'newsletter-subscription-settings', 'plugin_settings_page');
}

add_action('admin_menu', 'add_settings_page');
add_action('admin_init', 'plugin_settings');




function create_subscribed_emails_post_type() {
    register_post_type('subscribed_emails', array(
        'labels' => array(
            'name' => __('Subscribed Emails'),
            'singular_name' => __('Subscribed Email'),
        ),
        'public' => false,  // Set to true if you want it to be publicly accessible
        'has_archive' => false,
        'show_ui' => true,  // Display in the admin menu
        'supports' => array('title'),
    ));
}

add_action('init', 'create_subscribed_emails_post_type');
