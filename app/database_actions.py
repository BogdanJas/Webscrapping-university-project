import sqlite3

DATABASE = './twitterBot.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def insert_user_information(data, user_id):
    with get_db_connection() as conn:
        conn.execute('INSERT INTO User(Login, Password, LinkToPost, UserId) VALUES(?,?,?,?)',
                     (data['login'], data['password'], data['link_to_post'], user_id))
        conn.commit()


def get_user_information(user_id):
    with get_db_connection() as conn:
        result = conn.execute('SELECT * FROM User WHERE UserId = ? ORDER BY Id DESC LIMIT 1', (user_id,)).fetchone()
        return dict(result)


def insert_post_information(CreatorAccount, Text, HasPhoto, Photo, Comments, Reposts, Likes, Views, Bookmarks, PostDate,
                            PostTime):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Post(CreatorAccount, Text, HasPhoto, Photo, Comments, Reposts, Likes, Views, '
                       'Bookmarks, PostDate, PostTime) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                       (CreatorAccount, Text, HasPhoto, Photo, Comments, Reposts, Likes, Views, Bookmarks, PostDate,
                        str(PostTime)))
        conn.commit()
        return cursor.lastrowid


def insert_comment_information(Comment, PostId, user_id):
    with get_db_connection() as conn:
        conn.execute('INSERT INTO GeneratedComment(PostId, Comment, UserId) VALUES(?,?,?)',
                     (PostId, Comment, user_id))
        conn.commit()


def get_post_information(user_id):
    with get_db_connection() as conn:
        result = conn.execute(
            'SELECT p.CreatorAccount, p.Text, p.HasPhoto, p.Photo, p.Comments, p.Reposts, p.Likes, p.Views, p.Bookmarks, p.PostDate, p.PostTime FROM POST p INNER JOIN GeneratedComment c ON c.PostId = p.Id WHERE c.UserId = ? ORDER BY p.Id DESC LIMIT 1',
            (user_id,)).fetchone()
        return dict(result)


def get_comment(user_id):
    with get_db_connection() as conn:
        result = conn.execute('SELECT * FROM GeneratedComment WHERE UserId = ? ORDER BY Id DESC LIMIT 1',
                              (user_id,)).fetchone()
        return dict(result)
