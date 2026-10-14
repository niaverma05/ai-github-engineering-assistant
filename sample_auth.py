def delete_user(user, requesting_user):
    if user:
        database.delete(user.id)

    return {"message": "User deleted"}