<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>{{c.title}}</title>
    <description>{{c.desc}}</description>
    <link>{{c.link}}</link>
    <lastBuildDate>{{c.build_date}}</lastBuildDate>
    <pubDate>{{c.pub_date}}</pubDate>

% for i in items:
    <item>
        <title>{{i.title}}</title>
        <description>{{i.desc}}</description>
        % if i.link:
        <link>{{i.link}}</link>
        %end
        <guid isPermaLink="false">{{i.guid}}</guid>
        <pubDate>{{i.pub_date}}</pubDate>
    </item>
% end

</channel>
</rss>
