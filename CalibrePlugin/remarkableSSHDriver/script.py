import subprocess
import re
import http.client
from datetime import datetime
import json
from collections import deque

RM_IP='10.11.99.1'
RM_TUNNEL='calibre-remarkable-ssh'
RM_SSH=f'root@{RM_IP}'
RM_WEBUI=f'http://{RM_IP}'


def open_tunnel():
    ret = subprocess.run(['ssh', '-o', 'ConnectTimeout=5', '-S', RM_TUNNEL, '-q', '-f', RM_SSH, '-N']).returncode
    if ret == 0:
        print('ssh socker is open')
    else:
        raise Exception('ssh connection error')


def get_total_space():
    res = subprocess.run(['ssh', '-S', RM_TUNNEL, RM_SSH, 'df | grep "/home" | awk -F " " \'{print $2}\''], capture_output=True)
    return int(res.stdout, 10) * 1000


def get_free_space():
    res = subprocess.run(['ssh', '-S', RM_TUNNEL, RM_SSH, 'df | grep "/home" | awk -F " " \'{print $4}\''], capture_output=True)
    return int(res.stdout, 10) * 1000

date_time_str = '%Y-%m-%dT%H:%M:%S.%f'
def get_books():
    done_collections = set()
    collection_queue = deque([''])

    books = []
    while collection_queue:
        collection = collection_queue.pop()
        done_collections.add(collection)

        # http is implied, no need to use RM_WEBUI
        h1 = http.client.HTTPConnection(RM_IP)
        h1.request('POST', f'/documents/{collection}', headers={'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive'})
        res = h1.getresponse()
        if res.status != 200:
            raise Exception('could not retrieve book info', res.reason)
        
        raw_body = res.read().decode()
        json_body = json.JSONDecoder().decode(raw_body)

        for entry in json_body:
            if entry['Type'] == 'DocumentType':
                date = datetime.fromisoformat(entry['ModifiedClient'].split('.', 1)[0])

                authors = []
                if entry['documentMetadata'] and entry['documentMetadata']['authors'] and entry['documentMetadata']['authors'] != ['null']:
                    authors = entry['documentMetadata']['authors']
                books.append((entry['VissibleName'], entry['ID'], date.timetuple(), int(entry['sizeInBytes']), authors))
            elif entry['Type'] == 'CollectionType' and entry['ID'] not in done_collections and entry['ID'] not in collection_queue:
                collection_queue.append(entry['ID'])

    return books


def get_book(name):
    print("Getting books")
    res = subprocess.run(['ssh', '-S', RM_TUNNEL, RM_SSH, 'find /home/root/.local/share/remarkable/xochitl/ -type f -name "*.metadata" -exec grep -qw "DocumentType" {} \; -exec grep "visibleName" {} \; -print'], capture_output=True)
    
    books = []

    decoded = res.stdout.decode('utf8').strip().split('\n')
    if not decoded or len(decoded) % 2 != 0:
        print("Wrong entry number: ", len(decoded))
        return books

    raw_entries = list(zip(decoded[0::2], decoded[1::2]))
    for raw_name, raw_id in raw_entries:
        name_search = re.search('"visibleName": "(.*)"', raw_name)
        name = name_search.group(1)

        id_search = re.search('/home/root/\.local/share/remarkable/xochitl/(.*)\.metadata', raw_id)
        id = id_search.group(1)
        books.append((name, id))

    return books


def upload_book(file):
    res = subprocess.run(['curl', '/dev/null', '--form', f'file=@"{file}"', 'http://10.11.99.1/upload'], capture_output=True)
    
    decoded = res.stdout.decode('utf8')
    if decoded != '{"status":"Upload successful"}':
        raise Exception('could not upload book at', file, decoded)
    

def remove_books(rm_ids):
    for rm_id in rm_ids:
        subprocess.run(['ssh', '-S', RM_TUNNEL, RM_SSH, f'rm -r /home/root/.local/share/remarkable/xochitl/{rm_id}*'])
    
    # restart system so it will forget about the deleted files
    subprocess.run(['ssh', '-S', RM_TUNNEL, RM_SSH, 'systemctl restart xochitl'])