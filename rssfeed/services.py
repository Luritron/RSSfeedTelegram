import feedparser, re
from django.utils import timezone
from time import mktime
from .models import Feed, ItemNews

def fetch_rss_feed():
    feeds = Feed.objects.filter(active=True)
    for feed in feeds:
        try:
            parse_feed = feedparser.parse(feed.url)
            if parse_feed.status != 200 or not parse_feed.entries:
                print(f"Failed to fetch or parse feed: {feed.name}. Status: {parse_feed.status}")
                continue
        except Exception as e:
            print(f"Error while fetching the feed {feed.name} ({feed.url}): {e}")
            continue

        # 1. mktime converts struct_time/tuple of 9 elements -> to a timestamp with seconds
        # 2. fromtimestamp converts timestamp to a naive datetime object
        # 3. make_aware converts naive datetime to an aware datetime object, based on the current TZ
        for entry in parse_feed.entries:
            published_date = timezone.make_aware(
                timezone.datetime.fromtimestamp(mktime(entry.published_parsed))
            )

            # Clean up description for specific feeds using regex
            description = entry.description
            if feed.id == 2:
                pattern = r'<br /><br />(.*?)<br /><br /><a'
                match = re.search(pattern, description)
                description = match.group(1) if match else description

            # Get or create the ItemNews object
            item, created = ItemNews.objects.get_or_create(
                feed=feed,
                title = entry.title,
                url = entry.link,
                defaults = {
                    'description': description,
                    'published_date': published_date,
                }
            )