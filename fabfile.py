from fabric.api import local
import random
from signalback.local_settings import SECRET_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME


def push_to_heroku():
    """
    This helps us deploy to Heroku. Builds a temp branch, copies the needed
    Heroky settings to settings.py, adds, commits, and pushed to Heroku
    master
    """
    
    # Create a new, disposable branch
    heroku_branch_name = 'heroku-build-%s' % random.randint(1, 1000)
    current_branch = local('git rev-parse --abbrev-ref HEAD', capture=True)
    local('git checkout -b %s' % heroku_branch_name)
    
    # Append our sensetive settings, out of 
    with open("signalback/settings.py", "a") as myfile:
        myfile.write("\n\nSECRET_KEY='%s'" % SECRET_KEY)
        myfile.write("\nAWS_ACCESS_KEY_ID='%s'" % AWS_ACCESS_KEY_ID)
        myfile.write("\nAWS_SECRET_ACCESS_KEY='%s'" % AWS_SECRET_ACCESS_KEY)
        myfile.write("\nAWS_STORAGE_BUCKET_NAME='%s'" % AWS_STORAGE_BUCKET_NAME)
        myfile.write("\nS3_URL='http://s3.amazonaws.com/%s/'" % AWS_STORAGE_BUCKET_NAME)
        myfile.write("\nSTATIC_URL=S3_URL")
        
        
    # Toss our temp settings in git and push to heroku
    local("git commit -a -m 'heroku build'")
    local("git push heroku %s:master --force" % heroku_branch_name)
    local("git checkout %s" % current_branch)
    local("git branch -D %s" % heroku_branch_name)
    
    print "Pushed temp branch, %s, to Heroku" % heroku_branch_name