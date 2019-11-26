import datetime
import json
import requests
import statistics
from pprint import pprint

class Maintainer(object):
    """
    Contains functionality for reporting maintainer stats from target org or repo URL
    """
    def __init__(self, args):
        """
        Initialize the Maintainer (APIv4) class object
        :param args: command line arguments aggregated by argparse
        :type args: obj
        """

        self.headers = dict(Authorization=f"token {args.gh_token}",)
        self.base_url = "https://api.github.com/graphql"

        # Command-Line arguments
        self.debug = args.debug
        self.user = args.gh_user
        self.repo = args.gh_repos
        self.token = args.gh_token
        self.branch = args.gh_branch
        self.org = args.gh_org

    def run_query(self, query, vars=None):
        """
        Establish connection with GitHub and return requested results
        Returns request as json type
        """
        # A simple function to use requests.post to make the API call.
        # NOTE: the json= section for using variables in the queries
        request = requests.post(self.base_url, json={'query': query, 'variables': vars}, headers=self.headers)
        if request.status_code == 200:
            return request.json()
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

    def get_rate_limit(self):
        """
        GraphQL query to retrieve current rate limit stats.
        """
        query = """
        {
            viewer {
                login
            }
            rateLimit {
                limit
                cost
                remaining
                resetAt
            }
        }
        """
        result = self.run_query(query)
        if self.debug:
            print("get_rate_limit(): ")
            pprint(result)
        rate_limit = result['data']['rateLimit']['remaining']
        resetsAt = result['data']['rateLimit']['resetAt']
        time_soon = datetime.datetime.strptime(resetsAt, "%Y-%m-%dT%H:%M:%SZ")
        time_now = datetime.datetime.utcnow()
        rate_limit_reset = str(round((time_soon - time_now).total_seconds()/60))

        return rate_limit, rate_limit_reset

    def get_discovery_metrics(self):
        """
        GraphQL query to retrieve:
        - Total Page Views      <see maintainer_v3.py>
        - Total Unique Visitors <see maintainer_v3.py>
        - Referring Sites       <see maintainer_v3.py>
        - Number of Github Stars
        """

    def get_usage_metrics(self):
        """
        GraphQL query to retrieve:
        - Number of Clones          <see maintainer_v3.py>
        - Number of Unique Cloners  <see maintainer_v3.py>
        - Number of Forks           <see maintainer_v3.py>
        """

    def get_retention_metrics(self):
        """
        GraphQL query to retrieve:
        - Total Contributor Count    <see maintainer_v3.py>
        - Number of commits
        - Days since last commit
        """
        if not self.branch:
            query = """
                query($owner: String!, $name: String!) {
                    repository(owner: $owner, name: $name) {
                        defaultBranchRef { 
                            target {
                                ... on Commit {
                                    history (first:1) {
                                        totalCount
                                        edges {
                                            node {
                                                ... on Commit {
                                                    commitUrl
                                                    committedDate
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            """
            variables = {
                "owner": self.org,
                "name": self.repo
            }
        else: 
            query = """
                query($owner: String!, $name: String!, $branch: String!) {
                    repository(owner: $owner, name: $name) {
                        object(expression: $branch) {
                            ... on Commit {
                                history (first:1) {
                                    totalCount
                                    edges {
                                        node{
                                            ... on Commit {
                                                commitUrl
                                                committedDate
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            """
            variables = {
                "owner": self.org,
                "name": self.repo,
                "branch": self.branch
            }

        # ACQUIRE
        result = self.run_query(query, variables)

        if self.debug:
            print("get_retention_metrics(): ")
            pprint(result)

        # EXTRACT
        total_commit_count, committedDate = 0,0
        if not self.branch:
            total_commit_count = str(result['data']['repository']['defaultBranchRef']['target']['history']['totalCount'])
            committedDate = str(result['data']['repository']['defaultBranchRef']['target']['history']['edges'][0]['node']['committedDate'])
        else: 
            total_commit_count = str(result['data']['repository']['object']['history']['totalCount'])
            committedDate = str(result['data']['repository']['object']['history']['edges'][0]['node']['committedDate'])

        # TRANSFORM
        # parse commit date into datetime object and calculate the diff.
        # divide by 86400 for days, 3600 for hours
        # returned string in format: 2019-10-24T03:29:08Z
        time_then = datetime.datetime.strptime(committedDate, "%Y-%m-%dT%H:%M:%SZ")
        time_now = datetime.datetime.utcnow()
        diff_time = time_now - time_then
        total_time_since_last_commit = round(diff_time.total_seconds()/86400, 2)

        return(total_commit_count, total_time_since_last_commit)

    def get_project_health_metrics(self):
        """
        GraphQL query to retrieve:
        - Number of Open Issues
        - Number of Open Pull Requests
        NOTE: Since number of Open Pull Requests has a conflicting state with 
              merged and closed Pull Requests, a second query is in place to run separately 
        GraphQL query2 to retrieve: 
        - Average PR Response Time
        """
        query = """
            query($owner: String!, $name: String!) {
                repository(owner: $owner, name: $name) {
                    pullRequests(first: 100, states: OPEN) {
                        totalCount
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                        nodes {
                            id
                            createdAt
                            number
                            title
                        }
                    }
                    issues(states:OPEN) {
                        totalCount
                    }
                }
            }
        """
        variables = {
            "owner": self.org,
            "name": self.repo
        }

        # ACQUIRE
        result = self.run_query(query, variables)

        # EXTRACT
        if self.debug:
            print("get_project_health_metrics():")
            pprint(result)
        total_open_issues = result['data']['repository']['issues']['totalCount']
        total_open_pull_reqs = result['data']['repository']['pullRequests']['totalCount']
        
        # Since we now need the data for pullRequest webhooks in the reverse order, we need to query again with different parameters 
        # ERROR: 'message': 'Field \'pullRequests\' has an argument conflict: {first:"100",states:"OPEN"} or {last:"100"}?'}]}
        #
        # timelineItem strings for pullrequest nodes: https://developer.github.com/v4/enum/pullrequesttimelineitemsitemtype/
        query2 = """
            query($owner: String!, $name: String!) {
                repository(owner: $owner, name: $name) {
                    pullRequests(last: 5) {
                        totalCount
                        pageInfo {
                            startCursor
                            hasPreviousPage
                        }
                        nodes {
                            title
                            timelineItems(last: 100, itemTypes:[REVIEW_REQUESTED_EVENT, READY_FOR_REVIEW_EVENT, REOPENED_EVENT, MERGED_EVENT, REVIEW_DISMISSED_EVENT]) {
                            nodes {
                                ... on ReviewRequestedEvent {
                                    __typename
                                    createdAt
                                    requestedReviewer {
                                        ...ReviewerInfo
                                    }
                                }
                                ... on ReadyForReviewEvent {
                                    __typename
                                    createdAt
                                }
                                ... on MergedEvent {
                                    __typename
                                    createdAt
                                }
                                ... on ReopenedEvent {
                                    __typename
                                    createdAt
                                }
                                ... on ReviewDismissedEvent {
                                    __typename
                                    createdAt
                                }
                            }
                        }
                    }
                }
            }
        }
        fragment ReviewerInfo on RequestedReviewer {
            ... on User {
                login
            }
        }
        """
        variables2 = {
            "owner": self.org,
            "name": self.repo
        }

        # ACQUIRE
        result2 = self.run_query(query2, variables2)
        if self.debug:
            pprint(result2)

        # TRANSFORM 
        all_nodes = []
        open_nodes = []
        all_times = []
        time_origin = datetime.datetime(1, 1, 1, 0, 0)
        open_prs = result['data']['repository']['pullRequests']['nodes']
        pull_requests = result2['data']['repository']['pullRequests']
        all_nodes.extend(pull_requests['nodes'])
        pr_create = time_origin
        pr_end = time_origin
        
        if pull_requests['totalCount'] > 0: 
            # Each PR object has a number of Events: https://developer.github.com/v4/object/pullrequest/
            # Current iteration for this statistic is simply the mean average time between: 
            #     Supported Pull Request Start Events: 
            #         PR Review Requested 
            #         PR Marked Ready for Review
            #         PR Reopened
            #      Supported Pull Request End Events:
            #         PR Merged 
            #         PR Declined
            # 
            # Other supported events can be added in the future, e.g. Issue Comments, Changes Requested or new Commits..
            # Timeline Nodes will have to be added to query2 in order to have this data 
            # see https://developer.github.com/v4/union/pullrequesttimelineitem/
        
            # Parse through currently open PRs
            for node in range(len(open_prs)):
                open_pr_start = datetime.datetime.strptime(open_prs[node]['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
                open_pr_time_now = datetime.datetime.utcnow()
                open_diff = open_pr_time_now - open_pr_start
                all_times.append(open_diff.total_seconds()/86400)

            #  For each pull request fetched 
            for node in range(len(all_nodes)):
                # For each event in the pull request's timeline items
                for item in pull_requests['nodes'][node]['timelineItems']['nodes']:
                    # Filter through each supported Start/End Event condition and assign start/end times
                    typename = item['__typename']
                    if typename == 'ReviewRequestedEvent':
                        # PR was created and review was requested
                        pr_create = datetime.datetime.strptime(item['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
                    if typename == 'ReopenedEvent':
                        # Override the pr_create string if submitter reopens PR 
                        pr_create = datetime.datetime.strptime(item['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
                    if typename == 'ReadyForReviewEvent':
                        # Override both previous cases if submitter marks the PR as ready for review
                        # (Start the clock!) 
                        pr_create = datetime.datetime.strptime(item['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
                    if typename == 'MergedEvent':
                        pr_end = datetime.datetime.strptime(item['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
                    if typename == 'ReviewDismissedEvent':
                        # Override the pr_end string if maintainer dismisses the PR 
                        pr_end = datetime.datetime.strptime(item['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
                # If PR was not insta-merged, add time diff to the list for mean calculation
                if time_origin not in (pr_create, pr_end):
                    # Transform datetime object into a usable format for calculating a mean
                    # diff time string format: 2019-10-24T03:29:08Z
                    if 0 == pr_create or 0 == pr_end:
                        diff = 0
                    else:
                        diff = pr_end - pr_create

                        # divide by 86400 for days, 3600 for hours
                        diff = diff.total_seconds()/86400
                    if diff >= 0: 
                        all_times.append(diff)
                    else: 
                        all_times.append(0)
            # And finally calculate the mean PR resolution times from the list. 
            if self.debug:
                print(f"all_times: {all_times}")
            total_average_time_for_pr = round(statistics.mean(all_times), 2)
        else:
            # Handle case for when no pull requests have been opened yet..
            total_average_time_for_pr = 0 

        return total_open_issues, total_open_pull_reqs, total_average_time_for_pr

    def get_org_velocity_metrics(self):
        """
        GraphQL query to retrieve:
        - Number of issues closed (past 2 weeks?) TODO
        - Number of reviews TODO
        - Number of code changes TODO

        TODO: Issue#27 Would like to be able to scope this function for an organization, not repo.
        https://github.com/tektronix/OSO-Tools-and-Automation/issues/27

        """
