#!/usr/bin/env bash

tar --exclude=".git" --exclude="__pycache__" --exclude="*.log" \
    --exclude="*.db" --exclude="*.sqlite*" --exclude="tts/" \
    --exclude="media/" --exclude="deps/" \
    -czf /tmp/config_backup_lean.tar.gz -C /config .

cd /tmp && python3 -m http.server 8126
