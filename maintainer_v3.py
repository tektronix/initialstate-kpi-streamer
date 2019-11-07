import datetime
import json
import requests
from github import Github
from pprint import pprint

class Maintainer(object):
    """
    Contains functionality for reporting maintainer stats from target org or repo URL
    """
    def __init__(self, args):
        """
        Initialize the Maintainer (APIv3) class object
        :param args: command line arguments aggregated by argparse
        :type args: obj
        """
        self.gh = Github(args.gh_token)

        # Command-Line arguments
        self.repo = args.gh_repos
        self.org_name = args.gh_org
        self.debug = args.debug

    def get_contributor_count(self, repo):
        """
        Query to retrieve Total Contributor Count stats
        Calls: GET /repos/:owner/:repo/contributors
        Return: github.PaginatedList.PaginatedList of github.NamedUser.NamedUser
        """
        contributors_count = repo.get_contributors().totalCount
        if self.debug:
            print("get_contributor_count():")
            print(contributors_count)

        return contributors_count

    def get_clone_count(self, repo):
        """
        Query to get Clone Count Totals
        Calls: GET /repos/:owner/:repo/traffic/clones
        Return: None of list of github.Clone.Clone
        """
        contents = repo.get_clones_traffic(per="week")
        if self.debug:
            print("get_clone_count():")
            pprint(contents)

        return contents['count'], contents['uniques']

    def get_fork_count(self, repo):
        """
        Query to get Forks Count
        Calls: GET /repos/:owner/:repo/forks_count
        Return: integer
        """
        forks_count = repo.forks_count
        if self.debug:
            print("get_fork_count():")
            print(forks_count)

        return forks_count

    def get_views_count(self, repo):
        """
        Query to get Total Page Views
        Calls: GET /repos/:owner/:repo/traffic/views
        Return: None or list of github.View.View
        """
        contents = repo.get_views_traffic(per="week")
        if self.debug:
            print("\nget_views_count():")
            pprint(contents)

        return contents['count'], contents['uniques']

    def get_referrer_count(self, repo):
        """
        Query to get top referrers
        Calls:   GET /repos/:owner/:repo/traffic/popular/referrers
        Query Return type: list of github.Referrer.Referrer 
        Function Return type: dictionaries of {referring site: total}, {referring site: unique}
        """
        contents = repo.get_top_referrers()
        if self.debug:
            print("get_referrer_count():")
            pprint(contents)
        total_dict, unique_dict = {}, {}
        for idx, ref in enumerate(contents):
            total_dict.update({ref.referrer : contents[idx].count})
            unique_dict.update({ref.referrer : contents[idx].uniques})

        return total_dict, unique_dict

    def get_star_count(self, repo):
        """
        Query to get stargazers
        Calls: GET /repos/:owner/:repo/stargazers
        Return: integer
        """
        star_count = repo.stargazers_count

        if self.debug:
            print("Total # of stars for {}: {}".format(self.repo, star_count))

        return star_count

    def get_discovery_metrics(self):
        """
        REST apiv3 query to retrieve:
        - Total Page Views <see maintainer_v3.py>
        - Total Unique Visitors <see maintainer_v3.py>
        - Referring Sites <see maintainer_v3.py>
        - Number of Github Stars ...DONE
        """
        gh=self.gh
        repo = gh.get_organization(self.org_name).get_repo(self.repo)

        total_views, unique_views = self.get_views_count(repo)
        total_referrals, unique_referrals = self.get_referrer_count(repo)
        total_stars = self.get_star_count(repo)

        return total_views, unique_views, total_referrals, unique_referrals, total_stars

    def get_usage_metrics(self):
        """
        REST api v3 query to retrieve:
        - Number of Clones <see maintainer_v3.py>
        - Number of Unique Cloners <see maintainer_v3.py>
        - Number of Forks <see maintainer_v3.py>
        """
        gh=self.gh
        repo = gh.get_organization(self.org_name).get_repo(self.repo)

        total_clones, unique_cloners = self.get_clone_count(repo)
        forks_count = self.get_fork_count(repo)
        contributor_count = self.get_contributor_count(repo)

        return total_clones, unique_cloners, forks_count, contributor_count

