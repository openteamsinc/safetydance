from rever.activities.command import command

$PROJECT = 'safetydance'
$ACTIVITIES = [
              'version_bump',  # Changes the version number in various source files (setup.py, __init__.py, etc)
              'changelog',  # Uses files in the news folder to create a changelog for release
              'tag',  # Creates a tag for the new version number
              'push_tag',  # Pushes the tag up to the $TAG_REMOTE
              'build_sdist',
              'ghrelease',  # Creates a Github release entry for the new tag
               ]
$CHANGELOG_FILENAME = 'CHANGELOG.rst'  # Filename for the changelog
$CHANGELOG_TEMPLATE = 'TEMPLATE.rst'  # Filename for the news template
$PUSH_TAG_REMOTE = 'git@github.com:quansight/safetydance.git'  # Repo to push tags to

$GITHUB_ORG = 'quansight'  # Github org for Github releases and conda-forge
$GITHUB_REPO = 'safetydance'  # Github repo for Github releases  and conda-forge


command('build_sdist', 'python setup.py sdist bdist_wheel')
