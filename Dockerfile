FROM php:5.6-apache
COPY config/php.ini /usr/local/etc/php/
COPY config/000-default.conf /etc/apache2/sites-available/000-default.conf
RUN docker-php-ext-install mysqli
RUN a2enmod rewrite
RUN mkdir /tmp/uploads
EXPOSE 80
#COPY duckiehunt.com/ /var/www/html/

