# Japaconsults application
More details coming soon

## Start backend app
- Install python3 and python3-pip
- run `pip -r install requirements.txt`
- `cd` to `src/backend` directory
- run the `uvicorn main:app --host IP --port DESIRED_PORT`
	- replace `IP`: with your desired IP `[localhost, 127.0.0.1, etc]`
	- replace `DESIRED_PORT`: with your desired port

> Have fun

## Summary
A business toolkit that simplifies business workflow, elevates collaboration, and supercharges communication. Share files, manage payments, and keep everyone in the loop seamlessly.

## Introduction

JAPA_APP is a comprehensive application designed to streamline japaconsults business operations by combining file sharing, payment processing, and messaging into a single, integrated platform. This versatile solution enhance collaboration, financial transactions, and communication between staff and clients in one seamless environment.

## Key Features

- __File Sharing__: The application allows users to Easily upload, organize, and share documents, images, and other files between staffs and clients. This Simplify's collaboration and makes customer support easier seemless by providing a secured centralized hub for all business digital assets.

- __Payment Processing__: The application facilitates secure financial transactions within the platform thereby providing __japaconsults__ the abiltity to create and manage invoices, process clients payments in a secured channel , and keep track of all business financial activities effortlessly using the  in-built analytics.

- __Messaging/Notes Sharing__: The application also provides a means to stay updated with staff and clients using the built-in messaging/note  sharing system. Send messages, share updates, and maintain clear and efficient communication, all within the same platform.

## Getting Started
- clone the repository to your local machine
- create a `.env` file at the root of the repository and provide values for the below parameters
```env
# FOR DATABASE
DATABASE_URI = ""

# FOR JWT
SECRET_KEY = ""
ALGORITHM = ""
TOKEN_EXPIRATION_TIME = 

# SMTP CONFIGURATIONS
SMTP_HOST = ""
SMTP_MAIL = ""
SMTP_PWD = ""
SMTP_PORT = ""

#  for rave payments
# RAVE ACCOUNT KEYS
RAVE_PUBLIC_KEY = ""
RAVE_SECRET_KEY = ""
RAVE_ENCRYPTION_KEY = ""

# RAVE ACCOUNT KEYS
LIVE_PUBLIC_KEY = ""
LIVE_SECRET_KEY = ""
LIVE_ENCRYPTION_KEY = ""

# RAVE ENDPOINTS FOR VERIFICATION
CHECKOUT_ENDPOINT = ""
VERIFY_BY_ID = ""
VERIFY_BY_REF = ""
BANK_TRANSFER_ENDPOINT = ""
```
- run this command on terminal _if not installed_
```bash
sudo apt install python3 python3-pip python3-venv nginx mysql-server -y
```

- create and activate virtual environment to install python packages
```
python3 -m venv venv && source venv/bin/activate
```
_make sure you're at the root of the repository_

- install packages in `requirements.txt`
```bash
pip install -r requirements.txt
```

## Routes / Endpoints

### Authentication
- `/auth`:
    - __Description__: Authenticates a user to grant access to their account.

    - __Action__: Verify's the user's credentials (typically email and password) and generate an authentication token upon successful login.
    
    - __Usage__: Users provide their email address and password.

        - __username__: The users email address
        - __password__: The users password

- `/auth/generate/emailToken`:
    - __Description__: Generates email token which can be used in verifying user email address or initiating a password change.

    - __Action__: It take the users email address and verify's if there's already and exisitng account tied to that mail address. If no record is found it returns __HTTP 404 status code__ denoting no user details found. If a matching user account is found it proceeds then to create the users access token which is sent to the users email address as well as returned.

    - __Usage__: User sends there email address as query parameter to the endpoint alongside the type of verification(new_user or password change).

        - __new user email verificaation__: Generating tokn for email verification.
        *`japaconsults.sammykingx.tech/auth/generate/emailToken?mail=useremail@gmail.com&verv_type=new_user`*

        - __Password change__: Generating email token for password change.
        *`japaconsults.sammykingx.tech/auth/generate/emailToken?mail=useremail@gmail.com&verv_type=password_change`*

- `/auth/verifyEmail`:

    - __Description__: Verify's the users email address encoded on the verification token.

    - __Action__: The token is recievd from the request and then validated, upond successfull token validation the __request user__ email encoded in the token is verified. In a situation where by the token validation fails, an __HTTP 400 status code__ is returned with the appropriate reason in the *`detail`* parameter.
    Their might be situations where by the __request_user__ email has already been verified from a __previous request verification initaited__. In this case, a __400 HTTP status code__ is returned with the message in the *`detail`* parameter.

    - __Usage__: The email token gotten from the `/auth/generate/emailToken` endpoint is passed as query paremeter.

        - __parameter__: *`token`*
        - __example request__: *`japaconsults.sammykingx.tech/auth/verifyEmail?token=userToken`*

- `/auth/changePassword`:
    - __Descrption__: Confirm a password reset and update the user's password

    - __Action__: The *`token`(gotten from a previous request to `/auth/generate/emailToken`)* alongside the new password *`new_pwd`* is received from the request payload. The token is first validated and on successfull validation the users password is changed to the password specified on the *`new_pwd`* property. In a situation where the token validation fails, an __HTTP 400 status code__ is returned with the message in the *`detail`* property.

    - __Usage__: The available parameters are as follows;

        - *`token`*: Token gotten from *`/auth/generate/emailToken`* endpoint
        - *`new_pwd`*: The new users password

    - __example_request__:
        - __Using curl__:\n
```bash

 curl -X 'PATCH'\n
'japaconsults.sammykingx.tech/auth/changePassword'
	-H 'accept: application/json'
	-H 'Content-Type: application/json'
	-d '{
			"token": "user_token",
			"new_pwd": "string",
		}'

```
- `*japaconsults.sammykingx.tech/auth/changePassword*`

- `/auth/logout`:
    - __Description__: Invalidates the users access token

    - __Action__: The users token is taken from the request and invalidated


### Documents
- `/documents/upload`:
    - __Description__: Uploads a file to google drive cloud storage.

    - __Action__:

    - __Usage__:


### Notes

### Invoices

### Users

### Online Payments

- __Bank Transfer__
- __Card Payments__

### Payments
