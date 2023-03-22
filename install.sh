#!/bin/bash

sudo systemctl disable rclone-sync.service
sudo cp -f ./rclone-sync.service /etc/systemd/system/rclone-sync.service
sudo systemctl daemon-reload
sudo systemctl enable rclone-sync.service
sudo systemctl start rclone-sync.service
