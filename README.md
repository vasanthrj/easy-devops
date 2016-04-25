# easy-devops


## Chef Dead Node Cleanup

This is a python code for cleaning up the regsitered dead nodes availabe with Chef server. Uses Chef's knife command-line for querying and managing the nodes.
It takes two arguments they are time (in minutes) considered as node is dead and knife.rb conf file. Tested in Chef 12.

` chef-deadclient-cleanup.py 5 /etc/chef/knife.rb `

