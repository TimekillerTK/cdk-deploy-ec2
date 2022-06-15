# NOTE: ONLY FOR TESTING THIS IS NOT SAFE TO USE FOR PROD WORKLOADS!!!

# shebang is added automatically by deploy_ec2.py
# this will install prerequesites for php

# Enable more recent version of PHP (and jq)
amazon-linux-extras disable php7.2
amazon-linux-extras enable php7.4
yum clean metadata
yum install jq php-cli php-pdo php-fpm php-json php-mysqlnd -y

# Install apache & activate
yum install httpd -y
systemctl enable --now httpd

# Download and install composer
cd /home/ec2-user
runuser -l ec2-user -c "php -r \"copy('https://getcomposer.org/installer', 'composer-setup.php');\""
runuser -l ec2-user -c "php -r \"if (hash_file('sha384', 'composer-setup.php') === '55ce33d7678c5a611085589f1f3ddf8b3c52d662cd01d4ba75c0ee0459970c2200a51f492d557530c71c15d8dba01eae') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;\""
runuser -l ec2-user -c "php composer-setup.php"
runuser -l ec2-user -c "php -r \"unlink('composer-setup.php');\""
mv composer.phar /usr/local/bin/composer

# stuff you probably SHOULDN'T be doing
chown -R ec2-user:ec2-user /var/www/html

# Install AWS SDK for PHP via composer
runuser -l ec2-user -c "cd /var/www/html && composer require aws/aws-sdk-php"

# copy site file to directory
runuser -l ec2-user -c "cp /home/ec2-user/data/site/phptest.php /var/www/html/index.php"