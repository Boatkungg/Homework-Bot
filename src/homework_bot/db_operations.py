async def get_classroom_secret(db, guild_id):
    db_query = await db.fetch_one(
        """
        SELECT * FROM servers
        WHERE ServerID = :server_id
        """,
        {"server_id": guild_id},
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
