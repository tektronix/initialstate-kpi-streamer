# Maintainer stats collector

 Python Utility for collecting repo statistics from GitHub and streaming results to an [Initial State Dashboard](https://www.initialstate.com/)  

 NOTE: Currently, both API v3 and API v4 are in use for this project. Ideally, API v4 would be exclusively used, but until the schema is complete, some metrics are unavailable and instead use PyGithub for API v3 access.



## About

Current Metrics this query engine supports:

#### **Discovery**  
Are people able to find my project(s)?  
* Rationale: We are interested in understanding the impact of activities on user engagement (blog posts, conference meetups, etc.)
  * Total Page Views
  * Total unique visitors
  * Referring Sites
  * GitHub Stars

#### Usage

Who is getting use from the project(s)?

* Rationale: 
  * Number of Clones
  * Number of Unique Cloners
  * Number of forks

#### Retention:

How active is the project(s)?

* Rationale: 
  * Total contributor count
  * \# of total commits
  * Days since last commit

#### Project Health:

How well is/are the project(s) being maintained?

* Rationale: 
  * \# of Open Issues
  * \# of Open Pull Requests
  * Average PR Response time

#### Organizational Velocity: 

* Rationale:
  * \# of issues closed recently
  * \# of reviews added
  * \# of code changes
  * \# of unique committers



## Installation

#### Requirements: 

Python3+ 

* Virtual environment setup: 

  `$ python3 -m venv .env`

* Activate environment before installing dependencies: 

  `$ source .env/bin/activate`

  NOTE: on Python3.8+ look for the activate scripts in `.env/Scripts/activate`

* Install project dependencies:

   `$(.env) pip install -r requirements.txt`

* Run the project for any tektronix repo: 

  `$(.env) python maintainer_stats.py --token <GITHUB_TOKEN> --repo <repo_name (e.g. numconverter)>`



## Initial State Setup

![Example Dashboard](./assets/ISS_exampledash.png)

The results of each query can be streamed as unique signals to be displayed in the Initial State tiles app! 



Sign up for an account on their webpage and create a new Stream Bucket...

![](./assets/ISS_createnew1.png)Once created,  your new dashboard will need some data!

You'll need to manually extract a few things from your Dashboard Settings Page...

Click Settings and Give your Dashboard a Name, you'll need this name later: 

* Bucket Key, e.g. 'ABCDEFG1282N'
* Access Key, e.g. 'ist_ArgadfsjkWWjdgdfsnf322k4nsdnfdsfds'
* Bucket Name, e.g. 'My Awesome Dashboard :rocket:'

These items can be fed to the maintainer_stats utility as command line arguments, OR you can export them into your environment variables: 

```
$(.env) export ISS_BUCKET_NAME='My Awesome Dashboard :rocket:'
$(.env) export ISS_BUCKET_KEY=`ABCDEFG1282N`
$(.env) export ISS_ACCESS_KEY='ist_ArgadfsjkWWjdgdfsnf322k4nsdnfdsfds'
```



Run the utility against your project, or list of projects to get some initial tiles to work with

```
$(.env) maintainer_stats/python maintainer_stats.py -r programmatic-control-examples

Retrieving results for... tektronix\programmatic-control-examples       [DONE]
Streaming results for...  tektronix\programmatic-control-examples to Initial State Bucket (GHExport)    (╯°□°)╯ ︵┻━┻!! [DONE]
```



And Behold, you can now begin formatting your dashboard to your hearts content using the 'Edit Tiles' button. 

Check out the Initial State documentation for more information on all the cool things you can do. 

* [Initial State: Customize Your Tiles Dashboard](https://support.initialstate.com/hc/en-us/articles/360003879391-2-Customize-Your-Tiles-Dashboard)



## Usage

```
maintainer_stats.py [-h]   [-o --org GH_ORG] 
						   [-u --user GH_USER]
                           [-r --repo GH_REPOS [GH_REPOS ...]] 
                           [-t --token (or env: GITHUB_TOKEN)]
                           [-n --ISSBName (or env: ISS_BUCKET_NAME]
                           [-b --ISSBKey (or env: ISS_BUCKET_KEY)] 
                           [-i --ISSKey (or env: ISS_ACCESS_KEY)]
                           [-d, --debug]
```



### Supporting Links

[GitHub's REST API v3 developer page](https://developer.github.com/v3/)  
[GitHub's GraphQL API v4 developer page](https://developer.github.com/v4/)  
[PyGithub Documentation site](https://pygithub.readthedocs.io/en/latest/introduction.html)  
[Initial State](https://support.initialstate.com/hc/en-us)  

