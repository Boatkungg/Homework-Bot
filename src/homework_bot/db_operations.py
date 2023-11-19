async def get_classroom(db, guild_id):
    db_query = await db.fetch_one(
        """
        SELECT * FROM servers
        WHERE ServerID = :server_id
        """,
        {"server_id": guild_id},
    )

    return db_query


async def get_all_classrooms(db):
    db_query = await db.fetch_all(
        """
        SELECT * FROM servers
        """,
    )

    return db_query


async def add_classroom(db, guild_id, secret):
    await db.execute(
        """
        INSERT INTO servers (ServerID, ClassroomSecret)
        VALUES (:server_id, :secret)
        """,
        {"server_id": guild_id, "secret": secret},
    )


async def update_classroom(db, guild_id, secret):
    await db.execute(
        """
        UPDATE servers
        SET ClassroomSecret = :secret
        WHERE ServerID = :server_id
        """,
        {"server_id": guild_id, "secret": secret},
    )


async def get_user_password(db, guild_id, user_id):
    db_query = await db.fetch_one(
        """
        SELECT * FROM users
        WHERE UserID = :user_id 
        AND ServerID = :server_id
        """,
        {"user_id": user_id, "server_id": guild_id},
    )

    return db_query


async def add_user(db, guild_id, user_id, password):
    await db.execute(
        """
        INSERT INTO users (UserID, ServerID, Password)
        VALUES (:user_id, :server_id, :password)
        """,
        {
            "user_id": user_id,
            "server_id": guild_id,
            "password": password,
        },
    )


async def update_user(db, guild_id, user_id, password):
    await db.execute(
        """
        UPDATE users
        SET Password = :password
        WHERE UserID = :user_id
        AND ServerID = :server_id
        """,
        {
            "user_id": user_id,
            "server_id": guild_id,
            "password": password,
        },
    )


async def get_notify(db, guild_id, user_id):
    db_query = await db.fetch_one(
        """
        SELECT * FROM notify
        WHERE UserID = :user_id
        AND ServerID = :server_id
        """,
        {"user_id": user_id, "server_id": guild_id},
    )

    return db_query


async def get_all_notifies(db, guild_id):
    db_query = await db.fetch_all(
        """
        SELECT * FROM notify
        WHERE ServerID = :server_id
        """,
        {"server_id": guild_id},
    )

    return db_query


async def add_notify(db, guild_id, user_id, mode, before_due):
    await db.execute(
        """
        INSERT INTO notify (UserID, ServerID, Mode, BeforeDue)
        VALUES (:user_id, :server_id, :mode, :before_due)
        """,
        {
            "user_id": user_id,
            "server_id": guild_id,
            "mode": mode,
            "before_due": before_due,
        },
    )


async def update_notify_mode(db, guild_id, user_id, mode):
    await db.execute(
        """
        UPDATE notify
        SET Mode = :mode
        WHERE UserID = :user_id
        AND ServerID = :server_id
        """,
        {
            "user_id": user_id,
            "server_id": guild_id,
            "mode": mode,
        },
    )


async def update_notify_before_due(db, guild_id, user_id, before_due):
    await db.execute(
        """
        UPDATE notify
        SET BeforeDue = :before_due
        WHERE UserID = :user_id
        AND ServerID = :server_id
        """,
        {
            "user_id": user_id,
            "server_id": guild_id,
            "before_due": before_due,
        },
    )


async def delete_notify(db, guild_id, user_id):
    await db.execute(
        """
        DELETE FROM notify
        WHERE UserID = :user_id
        AND ServerID = :server_id
        """,
        {
            "user_id": user_id,
            "server_id": guild_id,
        },
    )
