#!/bin/bash
echo "Comencem a esperar"
while ! [ $(curl --write-out %{http_code} --silent --output /dev/null http://prestashop/) = 200 ]; do
    sleep 10
    echo "Encara esperem"
done
echo "Prestashop carregat"
curl http://prestashop/activate_webservice.php
echo "Webservice activat"
