FROM php:5.6-apache

# Sendmail
#RUN apt-get update && apt-get upgrade -y sendmail
#RUN echo "127.0.0.1 noreply.domain.com $(hostname)" >> /etc/hosts

RUN docker-php-ext-install mysqli
#RUN pecl install xdebug
#RUN docker-php-ext-enable xdebug
RUN a2enmod rewrite
RUN mkdir /tmp/uploads

# Install Composer + requirements
RUN apt-get -y update && apt-get install -y git
RUN curl -sS https://getcomposer.org/installer | php

# Copy composer files
COPY app/composer.* /var/www/html/

RUN php composer.phar install
RUN rm composer.phar

# Copy config files
COPY config/php.ini /usr/local/etc/php/
COPY config/000-default.conf /etc/apache2/sites-available/000-default.conf

# Copy app files
COPY app /var/www/html/

EXPOSE 80
