from django.db import models

# Create your models here.
class Feed(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} ({self.active})'

class ItemNews(models.Model):
    feed = models.ForeignKey(Feed, related_name='news_items', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    url = models.URLField()
    published_date = models.DateTimeField()

    def __str__(self):
        return f'{self.title} - {self.feed.name}'
