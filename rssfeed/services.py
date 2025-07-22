import feedparser, re
from django.utils import timezone
from time import mktime
from .models import Feed, ItemNews

class FeedParser:
    def __init__(self):
        self.cleaners = {
            2: self._clean_description_feed_2,
        }

    def _clean_description_feed_2(self, description):
        pattern = r'<br /><br />(.*?)<br /><br /><a'
        match = re.match(pattern, description)
        return match.group(1) if match else description

    def _clean_description(self, feed_id, description):
        cleaner = self.cleaners.get(feed_id, lambda x: x)
        return cleaner(description)

    def _parse_date(self, entry):
        return timezone.make_aware(
            timezone.datetime.fromtimestamp(
                mktime(entry.published_parsed)
            )
        )

    def _parse_entry(self, feed, entry):
        published_date = self._parse_date(entry)
        description = self._clean_description(feed.id, entry.description)

        ItemNews.objects.get_or_create(
            feed = feed,
            title = entry.title,
            url = entry.link,
            defaults = {
                'description': description,
                'published_date': published_date,
            }
        )

    def _process_feed(self, feed):
        try:
            parse_feed = feedparser.parse(feed.url)
            if parse_feed.status != 200 or not parse_feed.entries:
                raise ValueError(f'Failed to fetch or parse feed: {feed.name}. Status: {parse_feed.status}')

            for entry in parse_feed.entries:
                self._parse_entry(feed, entry)

        except Exception as e:
            raise ValueError(f'Error processing feed {feed.name}: {e}')

    def fetch_rss_feeds(self):
        feeds = Feed.objects.filter(active=True)
        for feed in feeds:
            try:
                self._process_feed(feed)
            except Exception as e:
                raise ValueError(f'Error processing feed {feed.name}: {e}')
