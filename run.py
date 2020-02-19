import csv
import os
import pandas as pd
import json
import time
import asyncio
from bs4 import BeautifulSoup
from klangooclient.MagnetAPIClient import MagnetAPIClient
from clavisphilly.Contentv4API import Contentv4API
from helper import print_progress_bar, hms, join_csv_files, remove_output_files, get_list
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv("_config.env") 

ARC_TOKEN = os.getenv("ARC_TOKEN")
ARC_DOMAIN = os.getenv("ARC_DOMAIN")
KLANGOO_ENDPOINT =  os.getenv("KLANGOO_ENDPOINT")
KLANGOO_CALK = os.getenv("KLANGOO_CALK")
KLANGOO_SECRET_KEY =  os.getenv("KLANGOO_SECRET_KEY")
SLEEPING_TIME = int(os.getenv("SLEEPING_TIME"))
SIZE = int(os.getenv("SIZE"))

clavis_client = Contentv4API(ARC_TOKEN,ARC_DOMAIN)

klangoo_client = MagnetAPIClient(KLANGOO_ENDPOINT, KLANGOO_CALK, KLANGOO_SECRET_KEY)

def convert_string_to_csv(file_name, dict_data, headers):
    file_exists = os.path.isfile(file_name)
    with open (file_name, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)

        if not file_exists:
            writer.writeheader()
        
        writer.writerow(dict_data)

def main_handle(article_ids):
    result = clavis_client.gettopics(article_ids)
    if result is not None:
        clavis_process(result, article_ids)
        # klangoo_process(result)
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(klangoo_process(result))
        loop.run_until_complete(future)
    return
    
def clavis_process(response, article_ids):
    try:
        # Clavis headers 
        headers = ['id', 'website_url', 'headline', 'clavis_topics']
        for content_element in response['content_elements']:
            dict_data = {}
            string_topics = ""
            try:
                for topic in content_element['taxonomy']['topics']:
                    string_topics += ("|" if len(string_topics) > 0 else "") + topic['name']
            except:
                pass

            article_id = content_element['_id']

            try:
                headline = content_element['headlines']['basic']
            except:
                headline = ""

            try:
                website_url = "inquirer.com"+content_element['website_url']
            except:
                website_url = ""

            dict_data.update({
                "id": article_id,
                "clavis_topics": string_topics,
                "website_url": website_url,
                "headline": headline
            })

            convert_string_to_csv("_output/clavis_topics.csv", dict_data, headers)

            article_ids.remove(article_id)

        if len(article_ids) > 0:
            for article_id in article_ids:
                dict_data.update({
                    "id": article_id,
                    "clavis_topics": "",
                    "website_url": "",
                    "headline": ""
                })
                convert_string_to_csv("_output/clavis_topics.csv", dict_data, headers)
    except Exception as error:
        print(error)
        return 

# Make asynchronous request to Klangoo, that will help us to increase the performance
async def klangoo_process(response): 
    input_requests = []
    try:
        # Klangoo headers
        headers = ['id', 'klangoo_topics']
        for content_element in response['content_elements']:
            article_id = content_element["_id"]
            dict_data = {}
            data_body_string = klangoo_handle_article_body(content_element)
            if data_body_string is not None:
                data_body_string_filtered = BeautifulSoup("""{}""".format(str(data_body_string)), "html.parser").get_text()

                input_requests.append({"body": data_body_string_filtered, "_id":article_id})
                # klangoo_topic(data_body_string_filtered, article_id, headers)

        with ThreadPoolExecutor(max_workers = SIZE) as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    klangoo_topic,
                    *(article['body'], article['_id'], headers)
                )
                for article in input_requests
            ]
            for response in await asyncio.gather(*tasks):
                pass

    except Exception as error:
        print(error)
        return

def klangoo_handle_article_body(data):
    arc_contents = ""
    contents = data.get('content_elements')
    if contents is not None:
        try:
            for element in contents:
                if element.get('type') == 'text':
                    if element.get('content') is not None:
                        arc_contents += ' ' + element['content']

            return arc_contents
        except Exception as error:
            print('An error occurred when handling article body for klangoo!')
            print(error)
            return None

def klangoo_topic(article_body, article_id, headers):
    if article_body is not None and len(article_body) > 10:
        request = { 
            'text' : article_body, 
            'format': 'json',
            'lang' : 'en'
        }
        number_of_tries = 0
        status = None
        response_json = None

        while status is None and number_of_tries < 3:   
            response = klangoo_client.callwebmethod('GetKeyTopics', request, 'POST')
            response_json = json.loads(response.decode("utf-8"))
            if response_json['status'] == 'OK':
                status = "OK"
            else:
                time.sleep(SLEEPING_TIME)
                number_of_tries += 1
            
        if response_json['status'] == 'OK':
            result = klangoo_parse_data(response_json, article_id)
            if result is not None:
                convert_string_to_csv("_output/klangoo_topics.csv", result, headers)
        else:
            # print('Error: \n', response)
            pass

def klangoo_parse_data(response, article_id):
    try:
        dict_data = {}
        string_topics = ""

        for topic in response['keyTopics']:
            string_topics += ("|" if len(string_topics) > 0 else "") + topic['text']

        dict_data.update({
            "id": article_id,
            "klangoo_topics": string_topics
        })

        return dict_data

    except Exception as error:
        print('An error occurred when parsing article body for klangoo!')
        print(error)
        return None

def handle_input():
    file_names = get_list()
    path = "_input/"
    for file in file_names:
        remove_output_files()
        file_name = path + file

        data = pd.read_csv(file_name) 
        total_rows = int(data.shape[0])
        print("Number of IDs: ", total_rows)

        if 'csv' in file:
            print('Handling the csv file named: ', file)
            count = 0
            array_data = []
            processed_total = 0
            f = open(file_name)
            csv_data = csv.reader(f)
            next(csv_data)
            for element in csv_data:
                if len(element[0]) > 1:        
                    array_data.append(element[0])
                    count -= -1
                    processed_total += 1

                    if count >= SIZE:
                        main_handle(array_data)
                        count = 0
                        array_data = []
                        time.sleep(SLEEPING_TIME)
                    else:
                        if processed_total == total_rows:
                            main_handle(array_data)
                    print_progress_bar(processed_total, total_rows, prefix = 'Progress:', suffix = 'Complete', length = 50)
            print("Going to join Clavis and Klangoo csv files!")
            join_csv_files()
            f.close()

if __name__ == "__main__":
    start = time.time()
    handle_input()
    total_time = hms(int(str(time.time()-start).split('.')[0]))
    print("The process took {}!".format(total_time))
    print("DONE ^^!")
