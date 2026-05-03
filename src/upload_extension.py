import os
import requests
from bs4 import BeautifulSoup

# credentials
username = os.getenv('GNOME_USERNAME')
password = os.getenv('GNOME_PASSWORD')
extension_zip_file = os.getenv('extension_zip_file')

if(username == ''):
	print('Username cannot be empty')
	exit(1)
if(password == ''):
	print('Password cannot be empty')
	exit(1)
if(extension_zip_file == ''):
	print('File cannot be empty')
	exit(1)

# Check if the file exists
if not os.path.exists(extension_zip_file):
	print("The file does not exist.")
	exit(1)

userAgent = 'GnomeShellExtensionUploader/1.0'

# URL for login
login_url = "https://extensions.gnome.org/accounts/login/"
upload_url = "https://extensions.gnome.org/upload/"
upload_post_url = "https://extensions.gnome.org/api/v1/extensions"

# 1. Load login page and obtain CSRF token
session = requests.Session()

# 2. Load login page
response = session.get(login_url)

# check if everything is ok
if response.status_code == 200:
	document = BeautifulSoup(response.text, 'html.parser')
	csrf_token = document.find('input', {'name': 'csrfmiddlewaretoken'})['value']

	print("Page: " + document.find('h3').text)

	# get CSRF token from cookies
	csrf_cookie = session.cookies.get('csrftoken')
else:
	print("Cannot load page.")
	exit(1)

# 3. Send login form on login page with CSRF token
login_data = {
	'username': username,
	'password': password,
	'csrfmiddlewaretoken': csrf_token
}
headers = {
	'Referer': login_url,
	'User-Agent': userAgent,
	'Cookie': f'csrftoken={csrf_cookie}',
	'Connection': 'keep-alive'
}
login_response = session.post(login_url, data=login_data, headers=headers)

if login_response.status_code == 200:
	document = BeautifulSoup(login_response.text, 'html.parser')

	#print("Page: " + document.find('h3').text

	errorMessage = document.find('ul', {'class': 'errorlist nonfield'})
	if(errorMessage):
		print(errorMessage.find("li").text)
		exit(1)
	print("Login was successed.")
else:
	print(f"Error in login: {login_response.status_code}")
	print(login_response.text)
	exit(1)


# 4. Load upload page
print('')
response = session.get(upload_url)

# check if everything is ok
if response.status_code == 200:
	document = BeautifulSoup(response.text, 'html.parser')
	csrf_token = document.find('input', {'name': 'csrfmiddlewaretoken'})['value']

	print("Page: " + document.find('h3').text)
else:
	print("Cannot load upload page.")
	exit(1)

# 5. Send upload form on upload page with CSRF token and file
upload_form_data = {
	'shell_license_compliant': 'on',
	'tos_compliant': 'on',
	'csrfmiddlewaretoken': csrf_token
}
headers = {
	'Referer': upload_url,
	#'Host': 'extensions.gnome.org',
	#'Origin': 'https://extensions.gnome.org/upload/',
	'User-Agent': userAgent,
	'Connection': 'keep-alive',
}
files = {'source': open(extension_zip_file, 'rb')}

# 6. Send POST request with data from form, CSRF token, headers, files, cookies
upload_response = session.post(upload_post_url, data=upload_form_data, headers=headers, files=files, cookies=session.cookies, timeout=60, allow_redirects=False)

# 7. Response
if upload_response.status_code == 200:
	print('')
	print("Upload was successed.")

	document = BeautifulSoup(upload_response.text, 'html.parser')
	errorMessage = document.find('p', {'class': 'message error'})
	if(errorMessage):
		print(errorMessage.text)
		exit(1)
if upload_response.status_code == 201:
	print('')
	print("Upload was successed.")

	document = BeautifulSoup(upload_response.text, 'html.parser')
	errorMessage = document.find('p', {'class': 'message error'})
	if(errorMessage):
		print(errorMessage.text)
		exit(1)
elif upload_response.status_code == 302:
	print('')
	print("Upload was successed.")
	print(f"Redirect detected. URL for redirect: {upload_response.status_code}")
	print(upload_response.headers['Location'])
elif upload_response.status_code == 504:
	print('')
	print("Upload was successed, but the server didn't respond in time.")
	print("504 Gateway Time-out")
else:
	print(f"Error in upload: {upload_response.status_code}")
	print(upload_response.text)
	exit(1)