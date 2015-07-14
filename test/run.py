import requests
import simplejson
import sys

server_path= 'http://localhost:5000/run'

if __name__ == '__main__':
    if len(sys.argv) > 0:
        path = sys.argv[1]
        js = open(path).read()
        json = simplejson.loads(js)
        response = requests.post(server_path, json=json)
        results = response.json()
        if results['status'] == 'ok':
            for i, track in enumerate(results['tracks']):
                print i + 1, track['title'], track['artist']
        else:
            print results['status']
