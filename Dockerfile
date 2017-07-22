FROM php:5.6-apache
COPY config/php.ini /usr/local/etc/php/
RUN docker-php-ext-install mysqli
RUN a2enmod rewrite
#COPY duckiehunt.com/ /var/www/html/

