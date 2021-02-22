# DailyApp

TransferApp is being upgraded to DailyApp

JSON files are replaced by Elasticsearch engine.  DailyApp and Elasticsearch engine are hosted in Docker containers, which can run on GCP Compute Engine or AWS EC2.

DailyApp implements a web service using Python/Flask framework.

For debugging and testing, use the default localhost and port 5000:
App.Run(port=5000,debug=False)

For production usage in the Cloud (GCP/AWS), change the IP and port number as follows:
App.Run(host='0.0.0.0',port=80)

For a test run, please visit: http://35.221.35.181

Enjoy!
