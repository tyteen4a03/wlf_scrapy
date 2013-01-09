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
        i = 0
        # Undo Quote HTML recursively
        for tag in soup.find_all("table",
            attrs={"width": "90%", "cellspacing": 1, "cellpadding": 3, "border": 0, "align": "center"}):
            i += 1
            username = tag.find("span", attrs={"class": "genmed"}).b.string
            if username == "Code:":
                quoteBB = "[code]" + br2nl(tag.find("td", attrs={"class": "code"}).string) + "[/code]"
                mode = "code"
            else:
                quoteBB = (('[quote="' + username.rstrip(": ")  + '"]') if username != "Quote: " else ("[quote]")) +\
                             br2nl(str(tag.find("td", attrs={"class": "quote"}))) + "[/quote]"
                mode = "quote"
            newContent.replace((QUOTE_HTML.format(username, mode, (tag.find("td", attrs={"class": mode}).string))), quoteBB)
        print "Occurances of [quote]/[code]: %s" % i
        i = 0
        # Undo tags with no attributes
        for tag, value in TAGS_NOATTR:
            for t in soup.find_all(tag):
                i += 1
                newContent.replace(str(t), ("[" + value + "]" + t.string + "[/" + value + "]"))
            if tag == "li": newContent.replace("[/*]", "")
        print "Occurances of [li]: %s" % i
        i = 0
        # Start undo tags with attributes
        # Undo URL
        for tag in soup.find_all("a"):
            if "href" not in tag:
                continue
            i += 1
            urlMode = ("email" if tag["href"].startswith("mailto:") else "url")
            theURL = "[" + urlMode + (
                ("]" + tag.string) if (tag["href"] == tag.string and not urlMode == "email") else ("=" + tag["href"] + "]" + tag.string)
                )  + "[/" + urlMode + "]"
            newContent.replace(str(tag), theURL)
        print "Occurances of [url]: %s" % i
        i = 0
        j = 0
        # Undo IMG tag
        for tag in soup.find_all("img"):
            # Check if it's a smiley
            imgBB = "[img]" + tag["src"] + "[/img]"
            newContent.replace(str(tag), imgBB)
            i += 1
            if tag["src"].find("http://pcpuzzle.com/forum/images/smiles/"):
                # Undo smiley
                smileyname = tag["src"].partition("http://pcpuzzle.com/forum/images/smiles/")[2][:-4]
                newContent.replace(imgBB, (":" + smileyname + ":"))
                j += 1
                continue
        print "Occurances of [img] (including smileys): %s" % i
        print "Occurances of smileys: %s" % j
        i = 0
        j = 0
        k = 0
        l = 0
        m = 0
        n = 0
        # Undo text elements (i.e <span>)
        for tag in soup.find_all(spanStyle):
            tagStyle = tag["style"]
            if tagStyle.startswith("color: "):
                # Color
                spanCode = "[color=" + tagStyle[6:] + "]" + tag.string + "[/color]"
                j += 1
            elif tagStyle.startswith("font-size: "):
                # Size
                fontSize = int(tag["style"].partition("font-size: ")[2].partition("px; line-height: normal")[0])
                if fontSize < 0 or fontSize > 29: # Invalid sizes
                    spanCode = tag.string
                else:
                    spanCode = "[size=" + str(fontSize) + "]" + tag.string + "[/size]"
                k += 1
            elif tagStyle == "font-weight: bold":
                # Bold
                spanCode = "[b]" + tag.string + "[/b]"
                l += 1
            elif tagStyle == "font-style: italic":
                # Italic
                spanCode = "[i]" + tag.string + "[/i]"
                m += 1
            elif tagStyle == "text-decoration: underline":
                # Underline
                spanCode = "[u]" + tag.string + "[/u]"
                n += 1
            else:
                # Not sure what this is, just ignore the whole tag
                print str(tag)
                continue
            newContent.replace(str(tag), spanCode)
            i += 1
        print "%s %s %s %s %s %s" % (i, j, k, l, m, n)
        # Undo <br />
        newContent = br2nl(newContent)
        print "Le Done"
        return newContent