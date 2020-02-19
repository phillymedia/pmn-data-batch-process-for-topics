import requests
import json

class Contentv4API:

    def __init__(self, token, url):
        self.token = token
        self.url = url
    
    def gettopics(self, article_ids):
        if len(article_ids) > 100:
            return 
        
        string_articles = ""

        for article_id in article_ids:
            string_articles += article_id + ","

        url = "https://api.pmn.arcpublishing.com/content/v4/ids"

        querystring = {
            "ids": string_articles,
            "website": "philly-media-network","included_fields":"taxonomy.topics,content_elements,headlines.basic,website_url"
        }

        headers = {
            'authorization': "Basic {}".format(self.token)
        }
        
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == 200:
            json_data = json.loads(response.text)
            return json_data
        else:
            print('An error occurred when sending request into Arc Server!')
            print(response.text)
            return None

