# -----------------------------------------------------------
# Script Name: gist_poll.py
#
# Usage:       gist_poll.py <github username> (Optional)
#
#! /usr/bin/env python3
# Parameters:
# GitHub Username - Optional
#                   If no parameters is entered, the  
#                   hardwired {user} variable will be used.
#
# Description: 
# Script is used to monitor a users github gists and 
# display details when a new gist has been published.
#
# Author:  Barry Jarman
# Date:    26 Nov 2019
# Version: v1.0
# Email:   barry.jarman@bazza.biz
# -----------------------------------------------------------

import requests
import json
import time
import sys
from datetime import datetime

_version = 1.0

arguments = len(sys.argv) - 1

if arguments != 1:
  user="bazza2000"
else:
  user=sys.argv[1]

# Explicitly request the v3 REST API version via the Accept header.
headers = {
    'Accept': "application/vnd.github.v3+json",
    }

def format_github_date (github_date):
  """Function to convert the GitHub date string to a more conventional readable output."""
  # fromisoformat doesnt fully support the ISO8601 date format so we have to replace the trailing Z
  created_at_tz_convert = github_date.replace("Z", "+00:00")
  # convert the formatted string into a datetime object for formatting.
  created_at_parsed = datetime.fromisoformat(created_at_tz_convert)
  # Return formatted datetime object for display.
  return created_at_parsed.strftime("%d/%b/%Y %H:%M:%S")

print ("Running", sys.argv[0], "Version:",_version)

# Check the user provided exists on github
check_user_url = f"https://api.github.com/search/users?q={user}"
try:
  response = requests.request("GET", check_user_url, headers=headers)
  if not response:
    print(f'Error Calling API\nHTTP Response Code {response.status_code}\nResponse Text: {response.text}')
    sys.exit(1)
except requests.exceptions.RequestException as e:
  print("Error calling API: ", e)
  sys.exit(1)

user_exists=response.json()['total_count']
if user_exists == 1:
  print (f"User \"{user}\" exists..continuing")
else:
  print (f"User \"{user}\" does not exist")
  sys.exit(1)


# public gists for the specified user
# GET /users/:username/gists
url = f"https://api.github.com/users/{user}/gists"

# Note: Due to polling rate restrictions of 60 polls per hour for unauthenticated user,
#       this value cannot be set lower than 60.
#       https://developer.github.com/v3/#rate-limiting
poll_delay = 60

# Get initial count of gists to use as reference for change.
try:
  response = requests.request("GET", url, headers=headers)
  # response equates to True if response was between 200 and 400, therefore, error if outside this range.
  if not response:
    print(f'Error Calling API\nHTTP Response Code {response.status_code}\nResponse Text: {response.text}')
    sys.exit(1)
except requests.exceptions.RequestException as e:
  print("Error calling API: ", e)
  sys.exit(1)

# Get the current number of entries (i.e. gists)
initial_num_gists=len(response.json())
initial_num_gists=1

# Repeated Loop to check and display any new Gists
# Loop until terminated with Ctrl-C
while True:
  try:
    response = requests.request("GET", url, headers=headers)
    if not response:
      print(f'Error Calling API\nHTTP Response Code {response.status_code}\nResponse Text: {response.text}')
      sys.exit(1)
  except requests.exceptions.RequestException as e:
    print("Error calling API: ", e)
    sys.exit(1)

  current_num_gists = (len(response.json()))
  print (f"Initial:{initial_num_gists} Current:{current_num_gists}")

  if initial_num_gists != current_num_gists:
      # Latest GIST is always the 1st element of the json response i.e. [0]
      latest_gist = response.json()[0]
      # Take the created_at value and reformat to more conventional readable output
      created_at = format_github_date(response.json()[0]['created_at'])
      # Gather description and html_url information from the json.
      description = response.json()[0]['description']
      html_url    = response.json()[0]['html_url']
      # Display the new GIST information to the console.
      print (f"New GIST has been created by {user} at {created_at}, with description of \"{description}\", accessed at {html_url}")
  time.sleep(poll_delay)
