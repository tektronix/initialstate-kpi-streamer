# -*- coding: UTF-8 -*-
"""
Python Utility for collecting repo statistics from GitHub and streaming results to an Initial State Dashboard
https://www.initialstate.com/

NOTE: Currently, both API v3 and API v4 are in use for this project. Ideally, API v4 would be exclusively used, but
until the schema is complete, some metrics are unavailable and instead use PyGithub for API v3 access.

REST API v3
https://developer.github.com/v3/

GraphQL API v4 (Subject to change!!)
https://developer.github.com/v4/

"""
import argparse
import maintainer_v3
import maintainer_v4
import os.path
from columnar import columnar
from ISStreamer.Streamer import Streamer

__name__ = '__main__'

def process_arguments():
    """
    Processes information needed to run the calculation

    :return:
    """
    parser = argparse.ArgumentParser(description='Maintainer stats utility')

    # required arguments
    parser.add_argument('-o ', '--org ',
                        action='store', dest='gh_org', default='tektronix',
                        help='GitHub Enterprise org URL (default: tektronix)')

    parser.add_argument('-u ', '--user ',
                        action='store', dest='gh_user', default='tektronix',
                        help='GitHub user')

    parser.add_argument('-b', '--branch ',
                        action='store', dest='gh_branch',
                        help='branch target')

    parser.add_argument('-r ', '--repo ',
                        nargs='+', dest='gh_repos', 
                        help='specific repo or list of repos (e.g. tpinux (default: <none>)')

    parser.add_argument('-t ', '--token',
                        action='store', dest='gh_token', default=os.environ.get('GITHUB_TOKEN', None),
                        help='GitHub API token (or env var GITHUB_TOKEN) (default: environment variable)')

    parser.add_argument('-n ' '--ISSBName ',
                        action='store', dest='iss_name', default=os.environ.get('ISS_BUCKET_NAME', None),
                        help='Initial State Stream Bucket Name (or env var ISS_BUCKET_NAME) (default: <none>')

    parser.add_argument('-k ' '--ISSBKey ',
                        action='store', dest='iss_bucket_key', default=os.environ.get('ISS_BUCKET_KEY', None),
                        help='Initial State Stream Bucket Key (or env var ISS_BUCKET_KEY) (default: <none>')

    parser.add_argument('-i ' '--ISSKey ',
                        action='store', dest='iss_key', default=os.environ.get('ISS_ACCESS_KEY', None),
                        help='Initial State Stream Access Key (or env var ISS_ACCESS_KEY) (default: <none>')

    parser.add_argument('-d ', '--debug ',
                        action='store_true', dest='debug',
                        help='enable debug logging (default: false)')

    parser.add_argument('-s','--small-terminal', action='store_true', dest='small_terminal',
                        help='disallow columnar from reporting for small terminals (e.g. Github actions)')

    return parser.parse_args()

if __name__ is '__main__':
    # Parse options
    args = process_arguments()

    # Initialize Maintainer GraphQL APIv4 class
    mtr4 = maintainer_v4.Maintainer(args)
    # Initialize Maintainer REST APIv3 class
    mtr3 = maintainer_v3.Maintainer(args)

    # Populate local variables
    repo_list = args.gh_repos
    iss_bucket_name = args.iss_name
    iss_bucket_key = args.iss_bucket_key
    iss_key = args.iss_key

    # Initial State the Initial State Streamer class
    if None not in (iss_key, iss_bucket_name, iss_bucket_key):
        streamer = Streamer(bucket_name=iss_bucket_name, bucket_key=iss_bucket_key, access_key=iss_key)
    else:
        if args.debug:
            print('!!! Initial State Streamer not initialized!!!!')
            print('Bucket Name {0}, Bucket Key {1}, Access Key {2}'.format(iss_bucket_name, iss_bucket_key, iss_key))

     # Prep the std out report columns
    report_data = []
    headers = ['repository', 'total views', 'unique views', 'total clones', 'unique clones', 'total stars', 'total forks',
                'contributors','total commits', '# Days since Commit', 'open issues', 'open PRs', 'Avg PR Response Time(days)']

     # Go Forth, retrieve the data from GitHub API spigots
    for repo in repo_list:
        print("Retrieving results for... {0}\{1}".format(args.gh_org, repo), end="\t", flush=True)
        mtr3.repo, mtr4.repo = repo, repo
        # Various Discovery Metrics (NOTE: GitHub APIv3)
        total_views, unique_views, total_referrals, unique_referrals, total_stars = mtr3.get_discovery_metrics()
        # Miscellaneous Usage Metrics (NOTE: GitHub APIv3)
        total_clones, unique_cloners, forks_count, contributor_count = mtr3.get_usage_metrics()
        # Assorted Retention Metrics (NOTE: GitHub APIv4)
        commits, time_since_last = mtr4.get_retention_metrics()
        # Disparate Project Health Metrics (NOTE: GitHub APIv4)
        total_open_issues, total_open_pull_reqs, total_average_time_for_pr = mtr4.get_project_health_metrics()
        # Rate Limit Left
        remaining_rate_limit, resetAt_rate_limit = mtr4.get_rate_limit()

        # Populate Report Data
        repo_data = [repo, total_views, unique_views, total_clones, unique_cloners, total_stars, forks_count,
                    contributor_count, commits, time_since_last, total_open_issues, total_open_pull_reqs, total_average_time_for_pr]
        report_data.append(repo_data)
        print("[DONE]")

        """
        Initial State Signal Creation and Streamer Logging
        """
        # Check if Initial State Streamer was created based on args provided (iss_key, iss_bucket etc.)
        # If not, don't try to create stream data.
        if not 'streamer' in dir():
            continue

        print("Streaming results for...  {1}\{2} to Initial State Bucket ({0})".format(iss_bucket_name, args.gh_org, repo), end="\t", flush=True)
        # Create ISS Traffic Signals
        iss_total_views = repo + "_total_views"
        iss_unique_views = repo + "_unique_views"
        # Iterate through referring sites until a full list is compiled into individual signals
        for key,val in total_referrals.items():
            streamer.log(repo + "_total_refer_from" + key, val)
        for key,val in unique_referrals.items():
            streamer.log(repo + "_unique_refer_from_" + key, val)
        iss_starcount = repo + "_total_stars"
        # Stream the ISS Traffic Signals
        streamer.log(iss_total_views, total_views)
        streamer.log(iss_unique_views, unique_views)
        streamer.log(iss_starcount, total_stars)
        print("(╯°□°)╯", end=" ", flush=True)
        streamer.flush()

        # Create ISS Usage Signals
        iss_total_clones = repo + "_total_clones"
        iss_unique_clones = repo + "_unique_clones"
        iss_forkcount = repo + "_total_forks"
        iss_contributors = repo + "_total_contributors"
        # Stream the ISS Usage Signals
        streamer.log(iss_total_clones, total_clones)
        streamer.log(iss_unique_clones, unique_cloners)
        streamer.log(iss_forkcount, forks_count)
        streamer.log(iss_contributors, contributor_count)
        print("︵", end="", flush=True)
        streamer.flush

        # Create ISS Retention Signals
        iss_commits = repo + "_total_commits"
        iss_time_since_commit = repo + "_time_elapsed_commits"
        # Stream the ISS Retention Signals
        streamer.log(iss_commits, commits)
        streamer.log(iss_time_since_commit, time_since_last)
        print("┻━┻", end="", flush=True)
        streamer.flush()

        # Create the ISS Project Health Signals
        iss_total_issues = repo + "_total_open_issues"
        iss_total_prs = repo + "_total_open_prs"
        iss_pr_resolution_time = repo + "_PR_response_time"
        # Stream the ISS Project Health Signals
        streamer.log(iss_total_issues, total_open_issues)
        streamer.log(iss_total_prs, total_open_pull_reqs)
        streamer.log(iss_pr_resolution_time, total_average_time_for_pr)
        print("!!", end="\t", flush=True)
        streamer.flush()
        print("[DONE]")
    # Close ISS Streamer
    if 'streamer' in dir():
        streamer.close()

    # Report the results to std out with columnar
    if not args.small_terminal:
        table=columnar(report_data, headers, row_sep='-', no_borders=True, justify=['l','c','c','c','c','c','c','c','c','c','c','c','c','c'])
        print(table)

    print(f"Rate Limit remaining: {remaining_rate_limit}, will reset in ~{resetAt_rate_limit}min")

