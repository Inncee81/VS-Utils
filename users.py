import pwd, grp
from prints import errmsg, debugmsg

## Get the username of the admin
def users_get_admin(all_users):
    users, admin = ([] for _ in range(2))
    for user in all_users:
        groups = [g.gr_name for g in grp.getgrall() if user[0] in g.gr_mem]
        gid = pwd.getpwnam(user[0]).pw_gid
        groups.append(grp.getgrgid(gid).gr_name)
        if "administrators" in groups:
            admin = user
        else:
            users.append(user)
    return (users, admin)

## Get all users of the Synology station
def users_get_selection(mode=0):

    ## Split users and admin
    all_users = pwd.getpwall()
    all_users = [(u[0],u[2]) for u in all_users if grp.getgrgid(u[3])[0] == 'users']
    all_users = [u for u in all_users if u[0] != 'admin' and u[0] != 'guest']
    (users, admin) = users_get_admin(all_users)

    ## Users
    if mode == 0:
        return users

    ## Users and admin
    elif mode == 1:
        return (users, admin)

    ## Admin only
    elif mode == 2:
        return admin
    else:
        errmsg("Could not identify users selection")
    return None

## Get the userID for a username (except admin)
def users_get_userid(username):
    users = users_get_selection()
    if(len(users) == 0):
        errmsg("Could not resolve the passed username (or admin)")
        return None
    user_id = [u[1] for u in users if u[0] == username]
    if(len(user_id) == 0):
        errmsg("Could not resolve the passed username (or admin)")
        return None
    return user_id[0]