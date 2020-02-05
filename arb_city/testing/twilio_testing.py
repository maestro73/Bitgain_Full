from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
#account_sid = 'ACaca0530e4b2efeb483ab6d2519c827b8'
#auth_token = '828fc311030c32fbf960b69d9d8f1e0b'
client = Client('ACaca0530e4b2efeb483ab6d2519c827b8', '828fc311030c32fbf960b69d9d8f1e0b')

message = client.messages.create(
			body="Arb City Test Failed",
			from_='+12054420287',
			to='+19733930439')

print(message.sid)