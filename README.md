# Coding Challenge App

A Flask app for aggregating data from Bitbucket and GitHub

## Install:

You can use a virtual environment :

``` 
pip install -r requirements.txt
```

## Running the code

* set two environment variables. These can be obtained in the provided JSON file, but are not stored in the repo for security. **If these variables are not set, a 401/403 error will be returned from the Bitbucket API:**

```
    BITBUCKET_CLIENT_ID=
    BITBUCKET_CLIENT_SECRET=
```

* start by spinning up the service:

```
python -m run 
```

You can then make requests to https:localhost:5000/:

`curl https:localhost:5000/<api_endpoint>`

## API Documentation

### Health Check

**Request**

`GET /health`

**Description**

Check health of app

**Response**

```json

{
    "response": "All Good!"
}
```

### Get Github Data

**Request**

`GET /github/<organization>`

Example: `/github/mailchimp/`

**Description**

Get repository level and organization level data from <organization> from GitHub.


**Response**

```json

{
    "repos": [
        {
            "watchers": 29,
            "forks": 1,
            "name": "ChimpKit2",
            "language": "Objective-C",
            "topic": "ChimpKit is Deprecated. Please see ChimpKit 2"
        },
        {
            "watchers": 6755,
            "forks": 2807,
            "name": "email-blueprints",
            "language": null,
            "topic": "Email Blueprints is a collection of HTML email templates that can serve as a solid foundation and starting point for the design of emails"
        },
        ...
        {
            "watchers": 24,
            "forks": 10,
            "name": "MailChimp.tmbundle",
            "language": "PHP",
            "topic": "MailChimp TextMate Bundle"
        }
    ],
    "repo_count": 29,
    "languages": [
        "JavaScript",
        "Python",
        "PHP",
        "Java",
        "HTML",
        "Objective-C",
        "CSS",
        "Kotlin",
        "Swift",
        "Ruby"
    ],
    "fork_count": 3404,
    "watcher_count": 7879
}
```

### Get Bitbucket Data

**Request**

`GET /bitbucket/<organization>`

Example: `/bitbucket/<organization>`

**Description**

Get repository level and organization level data from <organization> from Bitbucket.


**Response**

```json

{
    "repos": [
        {
            "watchers": 114,
            "forks": 77,
            "name": "mandrill-api-php",
            "language": "php",
            "topic": "A PHP 5.2+ compatible API client for the Mandrill email as a service platform."
        },
        ...
        {
            "watchers": 20,
            "forks": 17,
            "name": "mandrill-api-node",
            "language": "javascript",
            "topic": "A NodeJS API client for the Mandrill email as a service platform"
        }
    ],
    "repo_count": 10,
    "languages": [
        "python",
        "php",
        "javascript",
        "dart",
        "ruby"
    ],
    "fork_count": 326,
    "watcher_count": 384
}
```

### Get Merged Data

**Request**

`GET /merged/?org=x`

`GET /merged/?github=x&bitbucket=y`

Examples: 

`/merged/?org=mailchimp`

`/merged/?github=mailchimp&bitbucket=mailchimp`

**Description**

Get merged repository level and organization level data from both Bitbucket and GitHub. Provides organization as query parameters `org` or `github` & `bitbucket` to allow for different named orgs to be merged, in case the organization has a different name in both accounts.

**Parameters**

`org`: name of organization

`github`: name of organization in github

`bitbucket`: name of organization in bitbucket

**Note:** Either the use of `org=x` or `github=x&bitbucket=y` is required.

**Response**

```json

{
    {
    "Merged Totals": {
        "total_repos": 39,
        "languages": [
            "PHP",
            "Java",
            "Objective-C",
            "HTML",
            "Kotlin",
            "Python",
            "JavaScript",
            "CSS",
            "Swift",
            "Ruby",
            "python",
            "javascript",
            "php",
            "dart",
            "ruby"
        ],
        "total_forks": 3730,
        "total_watchers": 8263
    },
    "GitHub": {
        "repos": [
            {
                "watchers": 2,
                "forks": 0,
                "name": "mailchimp-transactional-ruby",
                "language": "Ruby",
                "topic": null
            },
            ...
            {
                "watchers": 5,
                "forks": 6,
                "name": "mailchimp-client-lib-codegen",
                "language": "HTML",
                "topic": null
            }
        ],
        "repo_count": 29,
        "languages": [
            "PHP",
            "Java",
            "Objective-C",
            "HTML",
            "Kotlin",
            "Python",
            "JavaScript",
            "CSS",
            "Swift",
            "Ruby"
        ],
        "fork_count": 3404,
        "watcher_count": 7879
    },
    "Bitbucket": {
        "repos": [
            {
                "watchers": 1,
                "forks": 4,
                "name": "mandrill-api-dart",
                "language": "dart",
                "topic": "A server and browser-compatible API client for the Mandrill email as a service platform."
            },
            ...
            {
                "watchers": 20,
                "forks": 17,
                "name": "mandrill-api-node",
                "language": "javascript",
                "topic": "A NodeJS API client for the Mandrill email as a service platform"
            }
        ],
        "repo_count": 10,
        "languages": [
            "python",
            "javascript",
            "php",
            "dart",
            "ruby"
        ],
        "fork_count": 326,
        "watcher_count": 384
    }
}
```

## What'd I'd like to improve on...

The Bitbucket api provides references links to get watcher and fork data. To make each of these calls for each repo in an organization, the api calls become very slow (> 15 seconds). I have implemented `asyncio` and `aiohttp` to speed up the api calls, and they are much faster now. However, these greatly increase the complexity of querying the Bitbucket API, and have lead to intermittent errors. I would love to figure out a way of querying the data efficiently without relying on asynchronous calls and decreasing the complexity.
