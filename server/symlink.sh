#!/bin/bash -x

echo "Removing current nginx configuration file" &&
sudo rm -rf /etc/nginx/nginx.conf &&
echo "Creating a symlink for nginx configuration file" &&
sudo ln -s /home/eisen/olaf/olafdjango/server/nginx.conf /etc/nginx/ &&
echo "Removing current site gunicorn service file" &&
sudo rm -rf /etc/systemd/system/gunicorn.service &&
echo "Creating a symlink for site gunicorn service file" &&
sudo ln -s /home/eisen/olaf/olafdjango/server/gunicorn.service /etc/systemd/system/ &&
echo "Removing current celery service file" &&
sudo rm -rf /etc/supervisor/conf.d/olaf-celery.conf
echo "Creating a symlink for celery service file" &&
sudo ln -s /home/eisen/olaf/olafdjango/server/olaf-celery.conf /etc/supervisor/conf.d/ &&
echo "Done. Symlinks created successfully"
