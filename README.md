# pmn-data-batch-process-for-topics
### `Overview`

pmn-data-batch-process-for-topics built by Python 3

This process handles a batch of article IDs then return the Clavis and Klangoo topics for those article IDs. The endpoints have used:
+ [Arc Content V4](https://arcpublishing.atlassian.net/wiki/spaces/CA/pages/50928390/Content+API)
+ [Klangoo GetKeyTopics Method](https://klangoosupport.zendesk.com/hc/en-us/articles/360015540371-GetKeyTopics-Method)

### `Set-up`

In the project directory, you can run:
```
virtualenv -p python3 venv
source venv/bin/activate
```
That will hep to create and active Python virtual environment.

When you still in the virtual environment, then install the libraries we will need to use for batch process:
```
pip install -r requirements.txt 
```
### `Configuration`

Before run the process, please update the `_config.env` file

```
ARC_DOMAIN = The Arc domain name.
ARC_TOKEN = The token for Arc authentication.
KLANGOO_SECRET_KEY = The Klangoo key for Klangoo authentication.
KLANGOO_CALK = The api key for Klangoo authentication.
KLANGOO_ENDPOINT = "https://magnetapi.klangoo.com/Service.svc"
SIZE = The number of posts will be processed at a time. It should be 0 < SIZE <= 40.
SLEEPING_TIME = Keeps the process slow down to avoid overload the Arc Server. It should be 2 <= SIZE <= 5.
```

### `Run the process`

For the current version, the process can handle the CSV input files only.

Please check that you already added the CSV input file into `_input` folder. The file name and header are up to you but it must be a CSV file and contains Article IDs.

<img src="https://hanson-storage.s3.amazonaws.com/input_batch_process.png" width="700"> 

Then, we are ready to fire:
```
python3 run.py
```
After the process has done, you can find the output in `_output` folder.
