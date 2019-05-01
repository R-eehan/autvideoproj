# Automate Debugger Project
The Automate Support team receive a lot of queries wherein users complain about video logs not being available for particular session(s) and are expected to debug the behaviour. However, they have to manually use REST API commands for individual session IDs to obtain the neccessary information.

This can be detrimental and cumbersome when there are a large number of session IDs to investigate.  

Thus, this project aims to aid the Automate Support team by obtaining a concise report/breakdown of all possible parameters/details in a particular user's session. All details that are usually obtained via individual REST API commands are now represented in a tabular format directly in the Engineer's local browser.

## Getting Started
The current version of the project is a POC and is open to optimization. Current version delivers the basic functionality expected of the application. 

### Prerequisites:
* Once you've downloaded/cloned the repository on your local machine, make sure you use Python 3.5 and above as your Project Interpreter. To check the version of Python3 you have on your local machine, use the following command: `python3 --v`

* In case you do not have Python3 installed, navigate to https://www.python.org/ and download the latest version for your machine. 

* The application runs on Flask, a micro web framework for Python. To install Flask, navigate to the directory and run: `pip3 install Flask`. For more information on Flask, [click here](http://flask.pocoo.org/).

* Once done, you should now be able to run the application on your local machine. 

* You can run the application via the Terminal of your machine as `python3 working_app.py` or choose an IDE of your choice and execute the same.

### Instructions and working:

The application accepts a CSV file containing all the session IDs of a particular user using BrowserStack's Automate/App Automate product.

This CSV file is to be obtained by executing a BigQuery command. The command is as follows:

```
 SELECT
 hashed_id
FROM
 [browserstack-1299:automate.partitioned_automation_session_stats]
WHERE
 _PARTITIONTIME >= "2019-04-28 00:00:00<start_date>"
 AND _PARTITIONTIME < "2019-05-01 00:00:00<end_date>"
 AND created_day >= "2019-04-28 00:00:00<start_date>"
 AND created_day < "2019-05-01 00:00:00<end_date>"
 AND group_id= <group_id>

```

**_Alter the BigQuery command as per your requirement i.e either for the Automate or App Automate product._**

**Note**: The format of the CSV file is predefined and you are expected to export the BigQuery information in the specified format. 

Here is a sample CSV file with the specified format: http://tiny.cc/d2ez5y

Steps to follow:

1. Navigate to 'localhost:8888'/'0.0.0.0:8888' on your local browser post executing the application(working_app.py).
2. Login with your BrowserStack Username and AccessKey. **Note**: This step is essential as these credentials will be used to gather the data to be rendered. 
3. Once successfully logged in, upload the CSV file and click on 'Submit'. If your CSV contains session IDs for App Automate, make sure you check the checkbox for App Automate. 
4. All necessary data should render in a tabular format. 

## Caveats

* The session IDs are queried sequentially and thus, the performance will be sub optimal. 

* Depending on the number of session IDs in the CSV file, the time taken for the output to render will vary. 

* In case your CSV file contains more than 100 session IDs, kindly divide your CSV file appropriately and proceed. 

* Only files with the '.csv' file extension can be uploaded.  
