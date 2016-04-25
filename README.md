# easy-devops


## Chef Dead Node Cleanup

This is a python code for cleaning up the regsitered dead nodes availabe with Chef server. Uses Chef's knife command-line for querying and managing the nodes.
It takes two arguments they are time (in minutes) considered as node is dead and knife.rb conf file. Tested in Chef 12.

` chef-deadclient-cleanup.py 5 /etc/chef/knife.rb `

## AWS Cloudformation Client helper script

Here the couple of scripts `aws-cloudformation-client-helper/Utils.py` and `aws-cloudformation-client-helper/propextractor.py` used for collecting the 
required parameter from a single parameter file and execute the cloudformation script. Templete executor will continoulsly poll for final state.
Finally writes the Cloudformation stack's Events, Outputs and Resources. 

Advantage of using these script are:
- No need open AWS Cloudformation console for checking the Stack event, outputs and resource created
- Manage using single parameter file if you are using multiple cloudformation scripts
- Utils.py script has function `createEc2KeyPairIfNotPresent` which is used to create ec2 key pair and private key key output will be written to a file.

`aws-cloudformation-client-helper/example/cfn-execute.py` contains sample usage of these helper script. 
