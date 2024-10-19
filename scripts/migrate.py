"""Migration script to move all users from one deployment to another"""

# plan
# download all Redis keys by prefix (use yarb?)
# upload to the new Redis while setting all "running" flags to false
# set
