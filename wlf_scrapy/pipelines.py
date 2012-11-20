# Wonderland Forum Scraping Bot made by tyteen4a03
# All rights reserved.

from wlf_scrapy.util import br2nl

QUOTE_HTML = '<table width="90%" cellspacing="1" cellpadding="3" border="0" align="center"><tr> 	  <td><span class="genmed"><b>%{username}s</b></span></td>	</tr>	<tr>	  <td class="%{mode}s">%{content}s</td>	</tr></table>'

TAGS_NOATTR = {
    "b": "b",
    "i": "i",
    "u": "u",
    "ul": "list",
    "li": "*",
    }

class Phpbb2ScrapyPipeline(object):
    def process_item(self, item, spider):
        print item

    def htmlToBBCode(self, content):
        """
        Turns resulting HTML to BBCode.
        """
        soup = BeautifulSoup(content)
        newContent = content
        # Undo Quote HTML recursively
        for tag in soup.find_all("table",
            attrs={"width": "90%", "cellspacing": 1, "cellpadding": 3, "border": 0, "align": "center"}):
            username = tag.find("span", attrs={"class": "genmed"}).b.string
            if username == "Code:":
                newContent = "[code]" + br2nl(tag.find("td", attrs={"class": "code"}).string) + "[/code]"
                mode = "code"
            else:
                newContent = (('[quote="' + username.rstrip(": ", 1)  + '"]') if username != "Quote: " else ("[quote]")) +\
                             br2nl(tag.find("td", attrs={"class": "quote"}).string) + "[/quote]"
                mode = "quote"
            newContent.replace((QUOTE_HTML % {"username": username, "mode": mode, "content": tag.find("td", attrs={"class": mode}).string}), newContent)
            # Undo tags with no attributes
        for tag, value in TAGS_NOATTR:
            for t in soup.find_all(tag):
                newContent.replace(str(t), ("[" + value + "]" + t.string + "[/" + value + "]"))
            if tag == "li": newContent.replace("[/*]", "")
            # Start undo tags with attributes
        # Undo URL
        for tag in soup.find_all("a"):
            if "href" not in tag:
                continue
            urlMode = ("email" if tag["href"].startswith("mailto:") else "url")
            theURL = "[" + urlMode + (
                ("]" + tag.string) if tag["href"] == tag.string and not urlMode == "email" else ("=" + tag["href"] + "]" + tag.string)
                )  + "[/" + urlMode + "]"
            newContent.replace(str(tag), theURL)
            # Undo IMG tag
        for tag in soup.find_all("img"):
            # Check if it's a smiley
            newContent.replace(str(tag), ("[img]" + tag["src"] + "[/img]"))
            # Undo
