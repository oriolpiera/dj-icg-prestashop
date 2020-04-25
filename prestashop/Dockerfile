FROM bitnami/prestashop
LABEL maintainer "Bitnami <containers@bitnami.com>"

# To activate Webservice
COPY activate_webservice.php /opt/bitnami/prestashop/activate_webservice.php
RUN install_packages vim phpunit php-mysqli libapache2-mod-php php-curl
                                         
