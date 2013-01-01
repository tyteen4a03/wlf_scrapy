# Wonderland Forum Scraping Bot made by tyteen4a03
# All rights reserved.

from bs4 import BeautifulSoup
from scrapy.spider import BaseSpider
from scrapy.http import FormRequest, Request

from wlf_scrapy.items import Attachment, Post, Topic, User
from wlf_scrapy.config import USERNAME, PASSWORD

EMPTY_CHAR = u'\xa0' # Used in parseUser, kind of a weird setting
EMPTY = (EMPTY_CHAR, None)

class WLFSpider(BaseSpider):
    name = "wlf"
    start_urls = ["http://pcpuzzle.com/forum/login.php"]
    real_start_urls = [
        "http://pcpuzzle.com/forum/viewforum.php?f=11",
        "http://pcpuzzle.com/forum/viewforum.php?f=12",
        "http://pcpuzzle.com/forum/viewforum.php?f=13",
        "http://pcpuzzle.com/forum/viewforum.php?f=26",
        "http://pcpuzzle.com/forum/viewforum.php?f=27",
        "http://pcpuzzle.com/forum/viewforum.php?f=28",
        ]

    root_domain = "http://pcpuzzle.com/forum"

    topics_to_ignore = []
    users_scanned = []
    smilies = {}

    def parse(self, response):
        """
        Login Magic.
        """
        return [FormRequest.from_response(response,
            formdata={'username': USERNAME, 'password': PASSWORD, 'autologin': 1},
            callback=self.afterLogin)]

    def afterLogin(self, response):
        # check login succeed before going on
        if "You have specified an incorrect or inactive username, or an invalid password." in response.body:
            self.log("Login failed", level=40)
            return
        # We've successfully authenticated, let's have some fun!
        else:
            # Get the smilies list for pipeline use
            yield Request("http://pcpuzzle.com/forum/posting.php?mode=smilies", callback=self.getSmilies)
            for link in self.real_start_urls:
                yield Request(link, callback=self.parseTopics, meta={"forumid": self.real_start_urls[0].split("=")[1]})
                # Convenient method for testing :P
                #yield Request("http://pcpuzzle.com/forum/download.php?id=41443", callback=self.parseAttachmentContent, meta={"postID": 24108, "attachment": Attachment()})
                #yield Request("http://pcpuzzle.com/forum/viewtopic.php?p=315144", callback=self.parsePosts, meta={"topicID": 24108})
                #yield Request("http://pcpuzzle.com/forum/profile.php?mode=viewprofile&u=8877", callback=self.parseUser)

    def parseTopics(self, response):
        soup = BeautifulSoup(response.body)
        # Find topic information
        for link, profileBit in zip(soup.find_all("span", attrs={"class": "topictitle"}),
            soup.find_all("span", attrs={"class": "name"})):
            if link.a["href"].split("=")[1] in self.topics_to_ignore: # Make sure Announcements and Stickies are not scanned twice
                continue
            aTopic = Topic()
            aTopic["forumID"] = response.meta["forumid"]
            aTopic["topicID"] = link.a["href"].split("=")[1]
            aTopic["topicName"] = link.a.string
            aTopic["posterID"] = profileBit.a["href"].split("=")[2]
            if "img" in link.children: del link.img
            if link.contents[0] in ["<b>Announecment:</b>", "<b>Sticky:</b>"]: # We've scanned this topic before, let's skip it in the future
                    self.topics_to_ignore.append(aTopic["topicID"])
            if aTopic["topicID"] not in self.topics_to_ignore:
                yield Request((self.root_domain + "/" + "viewtopic.php?t=" + aTopic["topicID"]),
                    callback=self.parsePosts,
                    meta={"topicID": aTopic["topicID"]})
            yield aTopic
        # Figure out if there's tomorrow
        hasMultiplePages = soup.find("td", align="right", valign="bottom", nowrap="nowrap")
        if hasMultiplePages:
            hasNextPage = hasMultiplePages.find("a", text="Next")
            if hasNextPage:
                yield Request((self.root_domain + "/" + hasNextPage["href"]),
                    callback=self.parseTopics,
                    meta={"forumid": response.meta["forumid"]})

    def parsePosts(self, response):
        """
        Parse post content.
        """

        soup = BeautifulSoup(response.body)

        def aName(tag):
            return tag.name == "a" and tag.has_key("name") and tag["name"] != "top"

        def aHref(tag):
            return tag.name == "a" and tag.has_key("href") and tag["href"].startswith("profile.php?mode=viewprofile&u=")

        def spanClass(tag):
            theList = [i for i in tag.strings]
            try:
                c = theList[0].find("Posted: ")
            except IndexError:
                return False
            return tag.name == "span" and tag.has_key("class") and c

        def spanClassPostBody(tag):
            return tag.name == "span" and tag.has_key("class") and tag["class"][0] == "postbody" and not (tag.renderContents().startswith("<br/>_________________<br/>"))

        def attachURL(tag):
            return tag.name == "a" and tag.has_key("href") and tag["href"].startswith("download.php?id=")

        def determineContentFetchMode(postid):
            if soup.find("a", href="posting.php?mode=editpost&p=" + postid):
                return "edit"
            elif (soup.find("a", href="posting.php?mode=quote&p=" + postid) and not "templates/subSilver/images/lang_english/reply-locked.gif" in response.body):
                return "quote"
            else:
                return "raw"

        # Find posts information
        for (pid, userid, username, posttime, content) in zip(
            soup.find_all(aName), # Post ID
            soup.find_all(aHref), # User ID
            soup.find_all("span", attrs={"class": "name"}),
            [[j for j in s.strings][0] for s in soup.find_all(spanClass)],
            soup.find_all(spanClassPostBody), # Post body
        ):
            aPost = Post()
            aPost["postID"] = pid["name"]
            aPost["topicID"] = response.meta["topicID"]
            aPost["posterID"] = userid["href"].partition("profile.php?mode=viewprofile&u=")[2]
            aPost["postTime"] = int(posttime.partition("Posted: ")[2])
            attachTable = content.find_next_siblings("table", attrs={"class": "attachtable"})
            # Attachment?
            if attachTable:
                for a in attachTable:
                    anAttachment = Attachment()
                    attachLink = a.find(attachURL)
                    anAttachment["postID"] = pid
                    anAttachment["displayFilename"] = a.find("span", attrs={"class": "gen"}) # The original name
                    anAttachment["attachmentID"] = attachLink["href"].split("=")[-1]
                    yield Request((self.root_domain + "/" + attachLink["href"]), callback=self.parseAttachmentContent,
                        meta={"attachment": anAttachment})
            # Initiate Post content scraping
            mode = determineContentFetchMode(aPost["postID"])
            if mode != "raw":
                yield Request((self.root_domain + "/" + "posting.php?mode=" +
                               ("editpost" if mode == "edit" else "quote") +
                               "&p=" + aPost["postID"]),
                    callback=self.parsePostContent,
                    meta={"mode": mode, "post": aPost, "username": username.b.string})
            else:
                aPost["content"] = ("raw", content)
                yield aPost
            # Initiate User scraping
            #if username.b.string not in self.users_scanned:
            #    yield Request((self.root_domain + "/" + userid["href"]),
            #        callback=self.parseUser)
        # Figure out if there's tomorrow
        hasMultiplePages = soup.find("td", align="left", valign="bottom", colspan=2)
        if hasMultiplePages:
            hasNextPage = hasMultiplePages.find("a", text="Next")
            if hasNextPage:
                yield Request((self.root_domain + "/" + hasNextPage["href"]),
                    callback=self.parsePosts,
                    meta={"topicID": response.meta["topicID"]})

    def parsePostContent(self, response):
        """
        Parses post content, if necessary.
        """
        # There are 3 modes of getting content from a post, they are Edit, Quote, and Raw.
        # Edit mode is the best mode since it preserves BBCode and smileys. However, it is not always available.
        # Quote mode is the most common mode to be used. It preserves the BBCode and smileys too, but requires stripping the extra
        # [quote] tag generated by phpBB.
        # The last mode (also the worst) is the Raw mode, in which the spider is required to go back to the post topic to get the contents.
        # In this mode, BBCode and Smileys are turned into raw HTML and is therefore harder to process.
        # This mode is required when the topic is locked.
        post = response.meta["post"]
        soup = BeautifulSoup(response.body)
        text = soup.find("textarea", attrs={"name": "message"})
        if response.meta["mode"] == "edit": # Edit mode - just pass the text on
            post["content"] = ("edit", text.string)
        else: # Quote mode
            post["content"] = ("quote", text.string[(10 + len(response.meta["username"])) :-8])
        return post

    def parseUser(self, response):
        """
        Parses user profile.
        """
        user = User()
        soup = BeautifulSoup(response.body)
        user["username"] = soup.find("th",
            attrs={"class": "thHead", "colspan": 2, "height": 25, "nowrap": "nowrap"}).string.lstrip(
            "Viewing profile :: ")
        user["userID"] = response.url.split("=")[-1]
        about, contact = soup.find_all("table", width="100%", border=0, cellspacing=1, cellpadding=3)[1:3]
        aboutTR = about.find_all("tr")
        contactTR = contact.find_all("tr")
        user["joinDate"] = about.find("td", width="100%").b.span.string
        user["totalPosts"] = aboutTR[1].find_all("span", attrs={"class": "gen"})[1].string
        user["location"] = aboutTR[2].find_all("span", attrs={"class": "gen"})[1]
        if user["location"] is not None:
            user["location"] = (user["location"].string if user["location"].string != EMPTY_CHAR else "")
        else:
            user["location"] = ""
        user["website"] = aboutTR[3].find_all("span", attrs={"class": "gen"})[1]
        if user["website"] is not None:
            user["website"] = (user["website"].b.a["href"] if user["website"].string != EMPTY_CHAR else "")
        else:
            user["website"] = ""
        user["occupation"] = aboutTR[4].find_all("span", attrs={"class": "gen"})[1]
        if user["occupation"] is not None:
            user["occupation"] = (user["occupation"].string if user["occupation"].string != EMPTY_CHAR else "")
        else:
            user["occupation"] = ""
        user["interests"] = aboutTR[5].find_all("span", attrs={"class": "gen"})[1]
        if user["interests"] is not None:
            user["interests"] = (user["interests"].string if user["interests"].string != EMPTY_CHAR else "")
        else:
            user["interests"] = ""
        user["email"] = contactTR[0].find_all("span", attrs={"class": "gen"})[1]
        if user["email"] is not None:
            user["email"] = (user["email"].a["href"].lstrip("mailto:") if user["email"].string != EMPTY_CHAR else "")
        else:
            user["email"] = ""
        user["msn"] = contactTR[2].find_all("span", attrs={"class": "gen"})[1]
        if user["msn"] is not None:
            user["msn"] = (user["msn"].string if user["msn"].string != EMPTY_CHAR else "")
        else:
            user["msn"] = ""
        user["yahoo"] = contactTR[3].find_all("span", attrs={"class": "gen"})[1]
        if user["yahoo"] is not None:
            user["yahoo"] = (user["yahoo"].a["href"].partition("http://edit.yahoo.com/config/send_webmesg?.target=")[2].partition("&.src=pg")[0] \
                             if user["yahoo"].string not in (EMPTY_CHAR, None) else "")
        else:
            user["yahoo"] = ""
        user["aim"] = contactTR[4].find_all("span", attrs={"class": "gen"})[1]
        if user["aim"] is not None:
            user["aim"] = (user["aim"].a["href"].partition("aim:goim?screenname=")[2].partition("&message=Hello+Are+you+there?")[0] if user["aim"].string != EMPTY_CHAR else "")
        else:
            user["aim"] = ""
        user["icq"] = contactTR[5]
        print dir(user["icq"])
        if user["icq"] is not None:
            user["icq"] = (user["icq"].noscript.a["href"].split("=")[-1] if user["icq"].string not in (EMPTY_CHAR, None) else "")
        else:
            user["icq"] = ""
        user["avatarName"] = soup.find("img", alt="", border=0)
        if user["avatarName"] is not None:
            user["avatarName"] = user["avatarName"]["src"].partition("images/avatars/")[2]
        self.users_scanned.append(user["username"])
        return user

    def parseAttachmentContent(self, response):
        """
        Grabs attachment content, then attach it to an Attachment.
        """
        attachment = response.meta["attachment"]
        attachment["fileContent"] = response.body
        return attachment

    def getSmilies(self, response):
        """
        Parses the Smilies page.
        """

        def smileyA(tag):
            return tag.name == "a" and tag.has_key("href") and (tag["href"].startswith("javascript:emoticon('"))

        soup = BeautifulSoup(response.body)
        for item in soup.find_all(smileyA):
            self.smilies[item.img["src"].split("/")[-1]] = item["href"].partition("javascript:emoticon('")[2].partition("')")[0]
        self.log("Smilies loaded.", level=20)

SPIDER = WLFSpider()