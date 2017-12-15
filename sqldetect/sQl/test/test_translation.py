#encoding=utf8

import json

def add_translation(data):
    if type(data) == dict:
        for i in data:
            data[i] = add_translation(data[i])
    elif type(data) == list:
        for i in data:
            i = add_translation(i)
    else:
        try:
            data = data.replace('\"', "\\\"")
        except:
            pass
    return data

if __name__ == "__main__" :
    data = [
        {
            "status": 1, 
            "type": 0, 
            "value": {
                "url": "http://demo.aisec.cn:80/demo/aisec/post_link.php", 
                "query": None, 
                "data": None
            }
        }, 
        {
            "status": 1, 
            "type": 1, 
            "value": [
                {
                    "dbms": None, 
                    "suffix": "", 
                    "clause": [
                        1, 
                        9
                    ], 
                    "notes": [], 
                    "ptype": 1, 
                    "dbms_version": None, 
                    "prefix": "", 
                    "place": "(custom) POST", 
                    "data": {
                        "1": {
                            "comment": "", 
                            "matchRatio": 0.915, 
                            "trueCode": 200, 
                            "title": "AND boolean-based blind - WHERE or HAVING clause", 
                            "templatePayload": None, 
                            "vector": "AND [INFERENCE]", 
                            "falseCode": 200, 
                            "where": 1, 
                            "payload": "----------105829879\nContent-Disposition: form-data; name=\"id\"\n\n1 AND 4843=4843\n----------105829879\nContent-Disposition: form-data; name=\"msg\"\n\nabc\n----------105829879\nContent-Disposition: form-data; name=\"B1\"\n\n\u00e6\u008f\u0090\u00e4\u00ba\u00a4\n----------105829879--"
                        }
                    }, 
                    "conf": {
                        "code": None, 
                        "string": "has this record.", 
                        "notString": None, 
                        "titles": None, 
                        "regexp": None, 
                        "textOnly": None, 
                        "optimize": None
                    }, 
                    "parameter": "MULTIPART id", 
                    "os": None
                }
            ]
        }
    ]
    print json.dumps(data) 
    print add_translation(data)
    print json.dumps(add_translation(data))
