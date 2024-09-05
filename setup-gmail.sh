#!/usr/bin/env sh

gcloud projects create gmail-tagging
gcloud services enable gmail.googleapis.com --project gmail-tagging
