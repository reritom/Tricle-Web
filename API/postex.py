#make arduino communication script
#upstart

#initialise
#create connection with arduino
#call /iaw every 10 minutes
#call api every

import requests
from base64 import b64encode


data = dict()
data['k1'] = 'tree'
data['k2'] = 'test'
data['k3'] = 'tank'
data['mode'] = 'scramble'

image = open('a.bmp', 'rb') #open binary file in read mode
image_read = image.read()
b64bytes = b64encode(image_read)
b64str = b64bytes.decode('utf-8')

uri = b64str


data['uri'] = uri


print(len(uri))

resp = requests.post('http://127.0.0.1:8000/api/remote/', json=data).json()

print(resp)
