<?php
define('_PS_ADMIN_DIR_', getcwd());
require(dirname(__FILE__).'/config/config.inc.php'); 
echo "Som-hi";
Configuration::updateValue('PS_WEBSERVICE', 1);
$apiAccess = new WebserviceKey();
$apiAccess->key = 'GENERATE_COMPLEX_KEY_LIKE_THIS!!';
$apiAccess->save();
$permissions = [
  'combinations' => ['GET' => 1, 'POST' => 1, 'PUT' => 1, 'DELETE' => 1, 'HEAD' => 1],
  'manufacturers' => ['GET' => 1, 'POST' => 1, 'PUT' => 1, 'DELETE' => 1, 'HEAD' => 1],
  'products' => ['GET' => 1, 'POST' => 1, 'PUT' => 1, 'DELETE' => 1, 'HEAD' => 1],
  'product_options' => ['GET' => 1, 'POST' => 1, 'PUT' => 1, 'DELETE' => 1, 'HEAD' => 1],
  'product_option_values' => ['GET' => 1, 'POST' => 1, 'PUT' => 1, 'DELETE' => 1, 'HEAD' => 1],
  'specific_prices' => ['GET' => 1, 'POST' => 1, 'PUT' => 1, 'DELETE' => 1, 'HEAD' => 1],
  'stocks' => ['GET' => 1, 'POST' => 1, 'PUT' => 1, 'DELETE' => 1, 'HEAD' => 1],
];
WebserviceKey::setPermissionForAccount($apiAccess->id, $permissions);
?>
