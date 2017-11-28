import os
import platform

##TODO Customise Commands for System Type
# Get System Type
SystemType = platform.system()

# Get All Tests
tests = dict()
for file in os.listdir('.'):
    if file.endswith(".json"):
        tests[file.split('.')[1]] = file.split('.')[0] 
# Get Number of Tests  
numTests = len(tests)

# Perform All Tests
##TODO show when error
for i in range(1,numTests):
    os.system("sls invoke --stage=dev --function=%s --path=test/mock_events/%s.%i.json"%(tests[str(i)], tests[str(i)], i))
