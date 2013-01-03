from wlf_scrapy import pipeline

CONTENT = """
<table width="90%" cellspacing="1" cellpadding="3" border="0" align="center"><tr> 	  <td><span class="genmed"><b>Quote:</b></span></td>	</tr>	<tr>	  <td class="quote"><span style="font-weight: bold"><span style="font-style: italic"><span style="text-decoration: underline">Content</span></span></span>
<br />
</td>	</tr></table><span class="postbody">
<br />

<br />
</span><table width="90%" cellspacing="1" cellpadding="3" border="0" align="center"><tr> 	  <td><span class="genmed"><b>Code:</b></span></td>	</tr>	<tr>	  <td class="code">A pile of code</td>	</tr></table><span class="postbody">
<br />

<br />
<ul>
<br />
<li>1
<br />
<li>3
<br />
</ul>
<br />

<br />
<img src="http://pcpuzzle.com/forum/templates/subSilver/images/logo_phpBB.gif" border="0" />  <img src="images/smiles/icon_wink.gif" alt="Wink" border="0" /> 
<br />

<br />
<a href="http://pcpuzzle.com/forum" target="_blank" class="postlink">http://pcpuzzle.com/forum</a>
<br />

<br />
<span style="font-size: 24px; line-height: normal"><span style="color: red">PCPUZZLE IS THE BEST!</span></span>
"""

if __name__ == "__main__":
    pipe = Phpbb2ScrapyPipeline()
    print pipe.htmlToBBCode(CONTENT)