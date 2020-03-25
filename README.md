# covid-19
Backtracking solution for infected risk
@copyright liu980299@gmail.com

# coronv
Coron Virus Risk Estimate Solution by backtracking contacting history and visiting places of the infected people.


This is a open project and welcomes anyone to commit to the solution and fight the virus. 

It is so horrible for the unknowing infected risk the person to be contacted and the place to visited (https://science.sciencemag.org/content/early/2020/03/13/science.abb3221).
As a result, there is no solution for restricting the individual people according to the infected risks but locking down the whole town/city/state/country. 
It is probably so harmful to the economy and society as the coronavirus itself. 


The solution is to provide a systemic way (config/policy) to predict the risk to be infected according to his contacting and visiting history. 

When a person is identified as a confirmed case, all persons in his contacted history (N dates before, could be configured) will be identified with some risk and applying the calculation to all contracted persons/places within the defined level of propagation.
When a person is identified as a negative case, all persons in his contacted history (N dates before, could be configured) will be rollback with some risk and applying the calculation to all contracted persons/places within the defined level of propagation.  

When propagation risk ratio is 1, it is whole city/town lockdown solution 

When progagation risk ration is 0, it is no restriction solution for virus transmission.

As different profile (whether willing to wear mask, washing hand regularly), the personal propagation risk is also different.

Contact time is also a factor of transmission.

As the culture for different regions are different, we migth use machine learning method to find the proper ratio for different regions.

We could make a policy based on the infected risk 
When the person is above 80% risk (TBD), he would be suggested to have a coronavirus test
When the person is above 50% risk (TBD), he would be suggested to have self-isolation
When the person is above 30% risk (TBD), he would be suggested to wear a mask
When the person is above 10% riks (TBD), he would be restricted from Aged people  

The solution is as below:

Frontend:
1. Using mobile to track your contacted persons by ultrasonic broadcast by date (probably keep history as 2 months) 
2. Using QRcode to identify the place registered to the system and tracking the history of visiting
3. if no connection to the internet, the phone will keep tracking history locally
4. if the heartbeat is not detected, the phone will alert user to restart app
5. Health officer to identify which person is infected and triggering backend risk 
6. Update the history to the server every minute
7. When the risk is above the different levels, alert different warning according to policies

Backend Risk propagation service :
1. After updating history to the server from phone and cross-check contact list. updating self history and the contacted phone and place history.
2. A scheduled task (every minute) to check phone status and send offline phone SMS to alert the user to restart the app
3. After triggering a confirm case, tag a status "Infected"  and run a propagation task to apply the risk to the defined levels 
4.  After triggering a negative case, tag a status "negative"  and run a propagation task to rollback the risk to the defined levels 
Note: to keep personal information as lest as possible, only mobile phone would be tracked in backend and front end only internal id would be tracked. 

Limitation:
1. add media router to force to use speaker instead of using bluebooth/headset etc
2. if the user stop app or someone not using the app, the tracking history might not be accurate (need the govnerment to force person to use the app to enter the places)
