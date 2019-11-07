# CONTRIBUTING
Thank you for your interesting in contributing to the initialstate-kpi-streamer, read on for details!

## Code of Conduct
First, please consult the [Tektronix Code of Conduct ](https://tektronix.github.io/Code-Of-Conduct/)
By participating you are expected to uphold this code. Please report unacceptable behavior to [opensource@tektronix.com](mailto:opensource@tektronix.com)

## GitHub API information
In an ideal world, this project would utilize a single API exclusively for retrieving GitHub Metrics. As the GraphQL API v4 develops, there are plans to replace all API v3 calls when the new API supports everything.  
In the meantime, reference documentation for APIv4 can be found here:
    * https://developer.github.com/v4/guides/intro-to-graphql/

An example query that accepts a repo owner, repo name and filepath as input, and then returns the contents of the file specified:  
```
query {
  repository(name: "repoName", owner: "repoOwner") {
    object(expression: "branch:path/to/file") {
      ... on Blob {
        text
      }
    }
  }
}
```


## How Can I Contribute?
### Report Issues
An example of a good Bug report will contain: 
* A clear descriptive title
* Exact steps to reproduce the issue
* Describe the Expected behavior and rationale for why you might've expected this
* Describe the Actual behavior observed after following the steps to reproduce
* Any other suporting evidence or details that you think might be helpful
### Feature Enhancements/Requests
An example of a good Feature request will contain: 
* A clear, descriptive title 
* If request is metric related, please submit in the form of the (CHAOSS Format) (Goal->Question->Metric) if possible!  
    e.g. From CHAOSS Metrics Code Development Focus Area:
    ```
     Goal: Efficiency - Learn how effective new code is merged into the code base.
     Question: How efficient is the project in reviewing proposed changes to the code, during a certain time period?
     Metric: Review Duration - What is the duration of time between the moment a code review starts and moment it is accepted?
    ```
    * https://chaoss.community/metric-review-duration/
### Pull Requests
Follow instructions in the [Pull Request Template](./.github/PULL_REQUEST_TEMPLATE.md) set up, in general, just submit your branch or fork against the master branch for review!

### Git Commit Messages
  * Use the present tense ("Adds feature" not "Added feature")
  * Limit to 72 characters
  * Consider starting the commit message with an applicable emoji:
    * :memo: when writing documentation
    * :beetle: when fixing a bug
    * :tada: when adding a new metric/query
    * :boom: when removing code
    * :speedboat: when adding performance enhancements
    * :octocat: etc...

## Contributor License Agreement
Contributions to this project must be accompanied by a Contributor License Agreement. You (or your employer) retain the copyright to your contribution; this simply gives us permission to use and redistribute your contributions as part of the project.

You generally only need to submit a CLA once, so if you've already submitted one (even if it was for a different project), you probably don't need to do it again.
