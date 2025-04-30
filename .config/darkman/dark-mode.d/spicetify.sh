#!/usr/bin/env bash

# Update spicetify and spotify using yay
yay -Syu --noconfirm spicetify-cli spotify

# Backup and apply spicetify configuration
spicetify backup apply
spicetify config current_theme catppuccin color_scheme mocha
spicetify -n apply
