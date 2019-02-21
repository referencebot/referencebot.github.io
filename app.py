import json
import os

import requests
import responder


api = responder.API()


RELEVANT_REPOS = [
    # 'IATI-Standard-SSOT',
    'IATI-Rulesets',
    'IATI-Extra-Documentation',
    'IATI-Codelists',
    'IATI-Codelists-NonEmbedded',
    # 'IATI-Developer-Documentation',
    # 'IATI-Guidance',
    'IATI-Websites',
]


RELEVANT_BASE_BRANCHES = [
    'version-2.03',
    'version-2.02',
    'version-2.01',
    'version-1.05',
    'version-1.04',
]


TRAVIS_URL = 'https://api.travis-ci.com/repo/referencebot%2F' + \
             'referencebot.github.io/requests'


@api.route("/github")
async def webhook(req, resp):
    data = await req.media()
    if data.get('action') != 'created':
        print('ignoring - not a creation event')
        return
    if not data.get('issue'):
        print('ignoring - not an issue')
        return
    if not data['issue'].get('pull_request'):
        print('ignoring - issue is not a PR')
        return
    if '@referencebot' not in data.get('comment', {}).get('body', ''):
        print('ignoring - comment not addressed to me!')
        return
    if data['issue']['state'] != 'open':
        print('ignoring - PR is not open')
        return
    comment_url = data['comment']['issue_url'] + '/comments'
    pr_url = data['issue']['pull_request']['url']
    pr_data = requests.get(pr_url).json()
    head_branch = pr_data['head']['ref']
    head_repo_url = pr_data['head']['repo']['clone_url']
    head_repo_name = pr_data['head']['repo']['name']
    base_branch = pr_data['base']['ref']
    base_repo_name = pr_data['base']['repo']['name']
    if base_repo_name not in RELEVANT_REPOS:
        print('ignoring - not a relevant repo')
    if base_branch not in RELEVANT_BASE_BRANCHES:
        print('ignoring - not a known base branch')
    travis_data = {
        'request': {
            'branch': 'master',
            'config': {
                'env': {
                    'GITHUB_API_URL': comment_url,
                    'HEAD_REPO_URL': head_repo_url,
                    'HEAD_REPO_NAME': head_repo_name,
                    'HEAD_BRANCH': head_branch,
                    'REPO_NAME': base_repo_name,
                    'VERSION': base_branch,
                }
            }
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Travis-API-Version': '3',
        'Authorization': 'token ' + os.environ['TRAVIS_TOKEN'],
    }
    print('Sending to travis...')
    r = requests.post(TRAVIS_URL, json=travis_data, headers=headers)
    print('Travis response: ' + r.reason)

    if r.status_code == 202:
        msg = f'Okay - no problem! :star: I\'ll build against ' + \
              f'{base_branch}.\n\nI\'ll post a link when it\'s ready.'
    else:
        msg = f'Err... I had some problem:\n\n{r.reason}'

    print(msg)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'token ' + os.environ['GITHUB_TOKEN'],
    }
    data = {
        'body': msg
    }
    r = requests.post(comment_url, json=data, headers=headers)
    print(r.status_code)


if __name__ == "__main__":
    api.run()
