import sqlite3

conn = sqlite3.connect('twitterBot.db')
print("Connected to database successfully")

conn.executescript("""
   CREATE TABLE User (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   Login VARCHAR(50) NOT NULL,
   Password VARCHAR(50) NOT NULL,
   LinkToPost VARCHAR(500) NOT NULL,
   UserId INTEGER NOT NULL
);

CREATE TABLE Post(
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    CreatorAccount VARCHAR(100),
    Text VARCHAR(300),
    HasPhoto BOOLEAN,
    Photo VARCHAR(500),
    Comments VARCHAR(20),
    Reposts VARCHAR(20),
    Likes VARCHAR(20),
    Views VARCHAR(20),
    Bookmarks VARCHAR(20),
    PostDate VARCHAR(20),
    PostTime varchar(20)
);

CREATE TABLE GeneratedComment (
  Id INTEGER PRIMARY KEY AUTOINCREMENT,
  PostId INTEGER NOT NULL,
  COMMENT VARCHAR(500) NOT NULL,
  UserId INTEGER NOT NULL,    
  FOREIGN KEY (UserId) REFERENCES User(UserId),
  FOREIGN KEY (PostId) REFERENCES Post(Id)
)""")
