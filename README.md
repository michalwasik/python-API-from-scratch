# API from scratch in python

## Describtion
  This is my first HTTP server written from basics. Server was created based on this article: https://bhch.github.io/posts/2017/11/writing-an-http-server-from-scratch/?fbclid=IwAR0BOuIjAsMOg-Z53bGXASOqQHkBHEsiZfdfi_pl9vbo_dhIFlBECTa_AvU. <br /><br />
  If you curious check continuation of this project idea at https://github.com/michalwasik/flask-racetrack where I created more appealing version using Flask.

# Goal
Main point of this project is to understand how HTTP server works without using any frameworks.
More specific to become familiar with:
* TCP server
* status codes
* HTTP requests
* scraping data


# How it works?

Main site is a list of race tracks form which you can chose one to add yours lap time.

![alt text](<list_tracks.png>)


If you had added data correctly all informations are being stored in JSON database. And after all these steps you can see yours and other users laptimes.

![alt text](<time_example.png>)
