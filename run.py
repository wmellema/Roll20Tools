import requests
import json
import os
import magic
asset_url = "https://app.roll20.net/image_library/marketplace_purchases_index"
image_request_url = "https://app.roll20.net/image_library/fetchsetresults/"
request_cookie = {"__cfduid":"ddbb26d1c3cad24bf986083f39108381b1530794967","_ga":"GA1.2.563149803.1530794970","_gid":"GA1.2.869601409.1539077289","rack.session":"ead60ab56f6363c55c1300ffb43c5dd89284661f135a797ad3dbf3b12426753f","roll20tempauth":"21"}

json_buffer = {}
if not os.path.exists("data.json"):
    req=requests.get(asset_url,cookies=request_cookie)
    print(req.text)
    done_keys = [0]
    for key,value in json.loads(req.text).items():
        if key == "free":
            for k,v in value.items():
                done_keys.append(int(k))
                textures = requests.get(image_request_url+str(k),cookies=request_cookie)
                json_buffer[v] = json.loads(textures.text)
    for i in range(10000):
        if i not in done_keys:
            textures = requests.get(image_request_url+str(i),cookies=request_cookie)
            if textures.status_code == 200:
                json_buffer[i] = json.loads(textures.text)
    
    print(json.dumps(json_buffer,indent=4))
    with open('data.json','w') as jsonfile:
        json.dump(json_buffer,jsonfile,indent=4)
json_buffer = json.load(open('data.json'))
for key,value in json_buffer.items():
    if not key:
        continue;
    try:
        directory_name = key.split("- ")[1].strip()
    except:
        directory_name = key
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)
    for k,v in value.items():
        try:
        # print(k)
        # print(json.dumps(v,indent=4))

            filename = (v['name']+"-"+k).replace("/"," ").replace("\\"," ")
            if os.path.exists(os.path.join(directory_name,filename)):
                continue
            req = requests.get(v['fullsize_url'], stream=True)
            req.raise_for_status()

            with open(os.path.join(directory_name,filename),'wb') as fd:
                for chunk in req.iter_content(chunk_size=50000):
                    fd.write(chunk)
            filename = (os.path.join(directory_name,filename))
            extention = magic.from_file(filename,mime=True).split("/")[1].strip()
            os.rename(filename,filename+"."+extention)
        except:
            print("Failed on:",k,v)
