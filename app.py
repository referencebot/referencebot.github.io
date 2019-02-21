from random import choice
import os

import requests
import responder


api = responder.API()


RELEVANT_REPOS = [
    # 'IATI-Standard-SSOT',
    'IATI-Rulesets',
    'IATI-Extra-Documentation',
    'IATI-Codelists',
    # 'IATI-Codelists-NonEmbedded',
    # 'IATI-Developer-Documentation',
    # 'IATI-Guidance',
    'IATI-Websites',
]


KNOWN_BASE_BRANCHES = [
    'version-2.03',
    'version-2.02',
    'version-2.01',
    'version-1.05',
    'version-1.04',
]


EMOJI = [
    '⭐️', '✨', '🌟', '👍', '🙌', '💅', '😸',
    '🔥', '💥', '⚡️', '🐨', '🐝', '🐜', '🐬',
    '🌈', '🎉',
]


EXCLAMATIONS = [
    'Okay - no problem!',
    'Okey dokey!',
    'On it!',
    'Righto!',
    'Gotcha!',
]


def random_exclamation():
    return choice(EXCLAMATIONS) + ' ' + choice(EMOJI)


def post_to_travis(env):
    travis_url = 'https://api.travis-ci.com/repo/referencebot%2F' + \
                 'referencebot.github.io/requests'
    travis_data = {
        'request': {
            'branch': 'master',
            'config': {
                'env': env,
            }
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Travis-API-Version': '3',
        'Authorization': 'token ' + os.environ['TRAVIS_TOKEN'],
    }
    resp = requests.post(travis_url, json=travis_data, headers=headers)
    return resp


def post_github_comment(comment, url):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'token ' + os.environ['GITHUB_TOKEN'],
    }
    data = {
        'body': comment
    }
    resp = requests.post(url, json=data, headers=headers)
    print(f'Github comment: "{comment}" ({resp.status_code})')
    return resp


def is_relevant(data):
    if data.get('action') != 'created':
        print('ignoring - not a creation event')
        return False
    if not data.get('issue'):
        print('ignoring - not an issue')
        return False
    if not data['issue'].get('pull_request'):
        print('ignoring - issue is not a PR')
        return False
    if '@referencebot' not in data.get('comment', {}).get('body', '').lower():
        print('ignoring - comment not addressed to me!')
        return False
    return True


@api.background.task
def process_data(data):
    if not is_relevant(data):
        return

    comment_url = data['comment']['issue_url'] + '/comments'

    if 'build' not in data['comment']['body'].lower():
        msg = 'Hi! How can I help? If you want me to build, just ' + \
              'mention my name and say "build".'
        post_github_comment(msg, comment_url)
        return

    if data['issue']['state'] != 'open':
        msg = 'Sorry - the pull request is closed so I can\'t build.'
        post_github_comment(msg, comment_url)
        return

    pr_url = data['issue']['pull_request']['url']
    pr_data = requests.get(pr_url).json()

    travis_env = {
        'GITHUB_API_URL': comment_url,
        'HEAD_REPO_URL': pr_data['head']['repo']['clone_url'],
        'HEAD_BRANCH': pr_data['head']['ref'],
        'REPO_NAME': pr_data['base']['repo']['name'],
        'VERSION': pr_data['base']['ref'],
    }

    if travis_env['REPO_NAME'] not in RELEVANT_REPOS:
        msg = 'Sorry - I\'m afraid I don\'t know how to build ' + \
              'this repository.'
        post_github_comment(msg, comment_url)
        return
    if travis_env['VERSION'] not in KNOWN_BASE_BRANCHES:
        msg = 'Sorry - the base branch doesn\'t look like a version ' + \
              'branch, so I\'m not sure how to proceed.'
        post_github_comment(msg, comment_url)
        return

    resp = post_to_travis(travis_env)

    if resp.status_code != 202:
        msg = f'Err... I had some problem:\n\n{resp.reason}'
        post_github_comment(msg, comment_url)
        return

    msg = f'{random_exclamation()} I\'ll build against ' + \
          f'{travis_env["VERSION"]}.\n\nI\'ll post a link ' + \
          f'when it\'s ready.'
    post_github_comment(msg, comment_url)


@api.route('/github')
async def webhook(req, resp):
    data = await req.media()
    process_data(data)
    resp.media = {'success': True}


if __name__ == '__main__':
    api.run()
