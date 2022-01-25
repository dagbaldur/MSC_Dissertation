from google.cloud import firestore
import json
import pandas as pd
from datetime import datetime

class IoT_Data():
    client = None
    collection = None
    project_id = "gcu-dissertation"    
    
    jwt = None

    def __init__(self):
        self.client = firestore.Client(project=self.project_id)
        self.collection = self.client.collection(u"IoT_ImageList")

    def getByDate(self,lower_date,upper_date,limit=1):
        lower_date = datetime.fromtimestamp(int(lower_date))
        upper_date = datetime.fromtimestamp(int(upper_date))
        
        docs = self.collection.where(u"time",u">=",lower_date).where(u"time",u"<=",upper_date).order_by(u"time",direction=firestore.Query.DESCENDING).limit(limit).stream()
        result = list(docs)
        print(len(result))
        return result


    def getAllByDevice(self,device,limit=None):
        if device is None:
            return None
        else:
            docs = self.collection.where(u'device',u'==',device).stream()
            result = list(docs)
            return result[0:limit]

    def getAllByRegistry(self,registry,limit=None):
        if registry is None:
            return None
        else:
            docs = self.collection.where(u'registry',u'==',registry).stream()
            result = list(docs)
            return result[0:limit]

    def getAnalyticsDevice(self,device):
        query_result = None

        docs = self.getAllByDevice(device)
        if len(docs) > 0:
            df = pd.DataFrame(list(map(lambda x: x.to_dict(),docs)))
            query_result = pd.concat([df.drop(['prediction'],axis=1),df['prediction'].apply(pd.Series)],axis=1)
            query_result['count'] = 1
            query_result['time'] = pd.to_datetime(query_result['time'])
            query_result['time'] = query_result['time'].dt.floor('H')
            
        return query_result

    def getAnalytics(self,registries):
        query_result = pd.DataFrame(columns=['registry', 'device', 'time', 'filename', 'crack', 'confidence'])
        registries = json.loads(registries)
        for ix in registries:
            reg = registries[str(ix)]
            docs = self.getAllByRegistry(reg['id'])
            if len(docs) > 0:
                df = pd.DataFrame(list(map(lambda x: x.to_dict(),docs)))
                
                if len(df) is not 0:
                    temp = pd.concat([df.drop(['prediction'],axis=1),df['prediction'].apply(pd.Series)],axis=1)
                #else:
                    query_result = pd.DataFrame.append(query_result,temp)
                    #query_result.append(pd.concat([df.drop(['prediction'],axis=1),df['prediction'].apply(pd.Series)],axis=1))
        
        query_result['count'] = 1
        query_result['time'] = pd.to_datetime(query_result['time'])
        query_result['time'] = query_result['time'].dt.floor('H')
        return query_result
