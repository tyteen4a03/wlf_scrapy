# Wonderland Forum Scraping Bot made by tyteen4a03
# All rights reserved.

from bs4 import BeautifulSoup

from util import br2nl

QUOTE_HTML = '<table width="90%" cellspacing="1" cellpadding="3" border="0" align="center"><tr> 	  <td><span class="genmed"><b>{0}</b></span></td>	</tr>	<tr>	  <td class="{1}">{2}</td>	</tr></table>'
TAGS_NOATTR = {
    "ul": "list",
    "li": "*",
    }

def spanStyle(tag):
    return tag.name == "span" and tag.has_key("style")

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
                quoteBB = "[code]" + br2nl(tag.find("td", attrs={"class": "code"}).string) + "[/code]"
                mode = "code"
            else:
                quoteBB = (('[quote="' + username.rstrip(": ")  + '"]') if username != "Quote: " else ("[quote]")) +\
                             br2nl(str(tag.find("td", attrs={"class": "quote"}))) + "[/quote]"
                mode = "quote"
            newContent.replace((QUOTE_HTML.format(username, mode, (tag.find("td", attrs={"class": mode}).string))), quoteBB)
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
                ("]" + tag.string) if (tag["href"] == tag.string and not urlMode == "email") else ("=" + tag["href"] + "]" + tag.string)
                )  + "[/" + urlMode + "]"
            newContent.replace(str(tag), theURL)
        # Undo IMG tag
        for tag in soup.find_all("img"):
            # Check if it's a smiley
            imgBB = "[img]" + tag["src"] + "[/img]"
            newContent.replace(str(tag), imgBB)
            if tag["src"].find("http://pcpuzzle.com/forum/images/smiles/"):
                # Undo smiley
                smileyname = tag["src"].partition("http://pcpuzzle.com/forum/images/smiles/")[2][:-4]
                newContent.replace(imgBB, (":" + smileyname + ":"))
        # Undo text elements (i.e <span>)
        for tag in soup.find_all(spanStyle):
            tagStyle = tag["style"]
            if tagStyle.startswith("color: "):
                # Color
                spanCode = "[color=" + tagStyle[6:] + "]" + tag.string + "[/color]"
            elif tagStyle.startswith("font-size: "):
                # Size
                fontSize = int(tag["style"].partition("font-size: ")[2].partition("px; line-height: normal")[0])
                if fontSize < 0 or fontSize > 29: # Invalid sizes
                    spanCode = tag.string
                else:
                    spanCode = "[size=" + str(fontSize) + "]" + tag.string + "[/size]"
            elif tagStyle == "font-weight: bold":
                # Bold
                spanCode = "[b]" + tag.string + "[/b]"
            elif tagStyle == "font-style: italic":
                # Italic
                spanCode = "[i]" + tag.string + "[/i]"
            elif tagStyle == "text-decoration: underline":
                # Underline
                spanCode = "[u]" + tag.string + "[/u]"
            else:
                # Not sure what this is, just ignore the whole tag
                continue
            newContent.replace(str(tag), spanCode)
        # Undo <br />
        newContent = br2nl(newContent)
        print "Le Done"
        return newContent