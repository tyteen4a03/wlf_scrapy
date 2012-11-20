# Wonderland Forum Scraping Bot made by tyteen4a03
# All rights reserved.

from scrapy.item import Item, Field

class Post(Item):
    """
    A post.
    """
    postID = Field()
    topicID = Field()
    posterID = Field()
    postTime = Field()
    content = Field()

class Attachment(Item):
    """
    An attachment, attached to a Post.
    """
    attachmentID = Field()
    postID = Field() # Parent post, user ID is omitted because it will be figured out by Post
    displayFilename = Field()
    #originalFilename = Field() # Records the filename listed, in case there's a filename conflict
    fileContent = Field()

class Topic(Item):
    """
    A topic.
    """

    topicID = Field()
    forumID = Field()
    posterID = Field()
    topicName = Field()

class User(Item):
    """
    A user.
    """

    userID = Field()
    username = Field()
    joinDate = Field()
    totalPosts = Field()
    avatarName = Field()
    location = Field()
    website = Field()
    occupation = Field()
    interests = Field()
    email = Field()
    msn = Field()
    aim = Field()
    yahoo = Field()
    icq = Field()
    signature = Field()