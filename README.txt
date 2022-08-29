Please download and install the listed dependencies on machine:
	https://www.mozilla.org/en-US/firefox/new/
	https://www.python.org/downloads/
	https://github.com/mozilla/geckodriver/releases (download and store in a new local folder named "driver")

To prep script for runtime, please run:
pip install -r requirements.txt

To run:
>    cd .\Desktop\GoogleBots_ShaunBahadori\


>	python.exe mapRun.py [instant]
	python.exe .\mapBot_Scheduler.py [scheduled run]

	or

	python.exe SEOBacklinkRun.py [instant]
	python.exe .\SEOBacklinkBot_Scheduler.py [scheduled run]



> For modifying scheduled run time/trigger

>mapBot_Scheduler.py
modify line 21

>SEOBacklinkBot_Scheduler.py
modify line 22

> with this template
scheduler.add_job(mainRun, 'cron', hour= <HOUR OF DAY TO START>, minute= <MINUTE OF DAY TO START>, max_instances=1)