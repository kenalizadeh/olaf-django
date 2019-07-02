#!/bin/bash -x

echo "Restarting nginx service..." &&
sudo systemctl restart nginx &&
echo "Restarting site gunicorn service..." &&
sudo systemctl restart gunicorn.service &&
echo "All services successfully restarted."