TV BOX video plugin for KODI.

This project is based on GNU v2 and shared on github.com to the community.

TV BOX is a plugin to watch multimedia content from remote servers in a XBMC (Kodi).

It can browse to pages (providers) or use remote lists.

A list could be used in M3U format or XML format.

An XML list must have this syntax:
```xml
<lists>
	<list>
		<name>My custom list</name>
		<description>My custom list description for TV BOX</description>
		<url>http://myremote.url/path/to/list,m3u</url>
		<format>m3u</format>
	</list>
	<list>
		<name>Other paths</name>
		<description>Other paths to get an structure</description>
		<url>http://myremote.url/path/to/structure.xml</url>
		<format>xml</format>
	</list>
</lists>
```
A list could be refereed to other list (for browse with a structure)

This addon has two main options:

	1) Static content (your list described before or an url to standard .m3u list)
	
	2) Web browsing by list