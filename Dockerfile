FROM php:5.6-apache
COPY config/php.ini /usr/local/etc/php/
COPY config/000-default.conf /etc/apache2/sites-available/000-default.conf

# Sendmail
#RUN apt-get update && apt-get upgrade -y sendmail
#RUN echo "127.0.0.1 noreply.domain.com $(hostname)" >> /etc/hosts

RUN docker-php-ext-install mysqli
RUN pecl install xdebug
RUN docker-php-ext-enable xdebug
RUN a2enmod rewrite
RUN mkdir /tmp/uploads
EXPOSE 80
#COPY duckiehunt.com/ /var/www/html/

