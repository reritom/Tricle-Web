import requests, io
from base64 import b64encode, b64decode
from PIL import Image
import sys

data = dict()
data['k1'] = 'that'
data['k2'] = 'heather'
data['k3'] = 'girl'
data['mode'] = 'unscramble'
data['userkey'] = '96835dd8bfa718bd6447'
data['token'] = '7dc89d8cfe3706653869'

url = 'http://127.0.0.1:8000/api/remote/'


image = open('b.bmp', 'rb') #open binary file in read mode

image_read = image.read()  #read binary bytes
b64bytes = b64encode(image_read)  #convert to b64 bytes
b64str = b64bytes.decode('utf-8') #convert to b64 string
uri = b64str
data['uri'] = uri

'''
headers = {'Content-type': 'multipart/form-data'}
files = {'media': image}
'''
try:
    resp = requests.post(url, json=data).json()
    print(resp)
except Exception as e:
    print(e)
    sys.exit(1)

if resp['valid'] == True:
    decoded = b64decode(resp['uri'])
    #print(decoded)
    stream = io.BytesIO(decoded)
    img = Image.open(stream)
    img.show()

#print(resp)
