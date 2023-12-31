async def create_db(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS guilds (
        GuildID BIGINT PRIMARY KEY,
        ClassroomSecret TEXT
        )
        """
    )

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
        UserID BIGINT PRIMARY KEY,
        GuildID BIGINT,
        Password TEXT,
        FOREIGN KEY (GuildID) REFERENCES guilds(GuildID)
        )
        """
    )

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS notify (
        UserID BIGINT PRIMARY KEY,
        GuildID BIGINT,
        Mode TEXT,
        BeforeDue INTEGER,
        FOREIGN KEY (GuildID) REFERENCES guilds(GuildID)
        )
        """
    )


async def get_guild(db, guild_id):
    db_query = await db.fetch_one(
        """
        SELECT * FROM guilds
        WHERE GuildID = :guild_id
        """,
        {"guild_id": guild_id},
    )

    return db_query


async def get_all_guilds(db):
    db_query = await db.fetch_all(
        """
        SELECT * FROM guilds
        """,
    )

    return db_query


async def add_guild(db, guild_id, secret):
    await db.execute(
        """
        INSERT INTO guilds (GuildID, ClassroomSecret)
        VALUES (:guild_id, :secret)
        """,
        {"guild_id": guild_id, "secret": secret},
    )


async def update_guild(db, guild_id, secret):
    await db.execute(
        """
        UPDATE guilds
        SET ClassroomSecret = :secret
        WHERE GuildID = :guild_id
        """,
        {"guild_id": guild_id, "secret": secret},
    )


async def get_user_password(db, guild_id, user_id):
    db_query = await db.fetch_one(
        """
        SELECT * FROM users
        WHERE UserID = :user_id 
        AND GuildID = :guild_id
        """,
        {"user_id": user_id, "guild_id": guild_id},
    )

    return db_query


async def add_user(db, guild_id, user_id, password):
    await db.execute(
        """
        INSERT INTO users (UserID, GuildID, Password)
        VALUES (:user_id, :guild_id, :password)
        """,
        {
            "user_id": user_id,
            "guild_id": guild_id,
            "password": password,
        },
    )


async def update_user(db, guild_id, user_id, password):
    await db.execute(
        """
        UPDATE users
        SET Password = :password
        WHERE UserID = :user_id
        AND GuildID = :guild_id
        """,
        {
            "user_id": user_id,
            "guild_id": guild_id,
            "password": password,
        },
    )


async def get_notify(db, guild_id, user_id):
    db_query = await db.fetch_one(
        """
        SELECT * FROM notify
        WHERE UserID = :user_id
        AND GuildID = :guild_id
        """,
        {"user_id": user_id, "guild_id": guild_id},
    )

    return db_query


async def get_all_notifies(db, guild_id):
    db_query = await db.fetch_all(
        """
        SELECT * FROM notify
        WHERE GuildID = :guild_id
        """,
        {"guild_id": guild_id},
    )

    return db_query


async def add_notify(db, guild_id, user_id, mode, before_due):
    await db.execute(
        """
        INSERT INTO notify (UserID, GuildID, Mode, BeforeDue)
        VALUES (:user_id, :guild_id, :mode, :before_due)
        """,
        {
            "user_id": user_id,
            "guild_id": guild_id,
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
        AND GuildID = :guild_id
        """,
        {
            "user_id": user_id,
            "guild_id": guild_id,
            "mode": mode,
        },
    )


async def update_notify_before_due(db, guild_id, user_id, before_due):
    await db.execute(
        """
        UPDATE notify
        SET BeforeDue = :before_due
        WHERE UserID = :user_id
        AND GuildID = :guild_id
        """,
        {
            "user_id": user_id,
            "guild_id": guild_id,
            "before_due": before_due,
        },
    )


async def delete_notify(db, guild_id, user_id):
    await db.execute(
        """
        DELETE FROM notify
        WHERE UserID = :user_id
        AND GuildID = :guild_id
        """,
        {
            "user_id": user_id,
            "guild_id": guild_id,
        },
    )
