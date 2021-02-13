def fetchYahoo(**args):
    
    import requests
    from urllib.parse import urlparse
    from datetime import datetime,timedelta 
    import pandas as pd
    import time
    
    if('sembol' not in args.keys()):
        return print('Sembol adı girilmedi! Örn: fetchYahoo(sembol = \'XU030.IS\')')
    sembol = args['sembol']
    
    if('start' not in args.keys()):
        return print('Başlangıç tarihi verilmedi! Örn: fetchYahoo(sembol = \'XU030.IS\',start=\'1.12.2020\')')

    if('end' not in args.keys()):
        return print('Bitiş tarihi verilmedi! Örn: fetchYahoo(sembol = \'XU030.IS\',end=\'2.12.2020\')')
    
    now = datetime.now()
    
    start = args['start']
    end = args['end']
    
    start = datetime.strptime(start, '%Y-%m-%d') if start != '' else datetime(2017, 1, 1)
    end = datetime.strptime(end, '%Y-%m-%d')
    
    #delta = now - timedelta(days=730)
    
    #start = delta if delta > start else start
    
    altCrumb = 'FK.eP1I.MKp'
    raw = requests.get('https://finance.yahoo.com/chart/'+sembol)
    matches = re.search(r"\,\"CrumbStore\"\:\{\"crumb\"\:\"([\w\d\.\-]+)\"\}\,\"Compo", raw.text, re.IGNORECASE)
    
    crumb = matches.group(1) if matches else altCrumb
    
    payload = {
        'symbol':sembol,
        'period1':str(int(time.mktime(start.timetuple()))),
        'period2':str(int(time.mktime(end.timetuple()))),
        'useYfid':'true',
        'interval':'1d',
        'includePrePost':'true',
        'events':'div%7Csplit%7Cearn',
        'lang':'tr-TR',
        'region':'TR',
        'crumb':crumb,
        'corsDomain':'finance.yahoo.com'
    }
    queryPoint = 'https://query1.finance.yahoo.com/v8/finance/chart/'+sembol
    
    r = requests.get(queryPoint, params=payload)
    
    data = r.json()

    if data[list(data.keys())[0]]['error'] is not None:
        return print("""
Bir hata var!
Hata Kodu: {kod}
Hata Açıklama: {aciklama}
        """.format(kod=data[list(data.keys())[0]]['error']['code'],aciklama=data[list(data.keys())[0]]['error']['description']))

    zamanlar = list(map(lambda x: datetime.fromtimestamp(int(x)).strftime('%Y-%m-%d'),data['chart']['result'][0]['timestamp']))
    data = pd.DataFrame(data['chart']['result'][0]['indicators']['quote'][0],columns={'open','close','high','low','volume'},index = zamanlar)
    
    generateIndex = pd.date_range(start = start,end = end, freq='1D')
    generateIndex = generateIndex.format(formatter=lambda x: x.strftime('%Y-%m-%d'))
    temp = pd.DataFrame(index=generateIndex)
    temp['sembol'] = sembol
    temp = pd.concat([data,temp],join='outer',axis=1)
    temp['sembol'] = sembol
    temp = temp.reset_index()
    temp = temp.rename(columns={"index": "tarih"})
    return temp
    
  
