from dating_DB import Session, MatchingUser, BlacklistedUser

def database_check(check_id):  # метод для проверки на вхождение в БД
    session = Session()

    liked_users = session.query(MatchingUser).all()
    liked_users_list = [liked_user.matching_id for liked_user in liked_users]

    disliked_users = session.query(BlacklistedUser).all()
    disliked_users_list = [disliked_user.blacklisted_id for disliked_user in disliked_users]

    if check_id in liked_users_list or check_id in disliked_users_list:
        return True
    else:
        return False