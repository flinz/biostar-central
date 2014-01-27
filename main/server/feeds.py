from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from main.server import models, const, html
from django.conf import settings
from django.contrib.sites.models import Site
from datetime import datetime, timedelta

#SITE = Site.objects.get(id=settings.SITE_ID)

class LatestEntriesFeed(Feed):
    title = "NeuroStarss.org latest!"
    link = "/"
    description = "Latest 25 posts from the NeuroStars server"

    def items(self):
        # the feed is delayed to reduce spam
        now = datetime.now()
        if 7 < now.hour < 20 :
            timestamp = now - timedelta(minutes=settings.FEED_DELAY)
        else:
            # slow down the feeds
            timestamp = now - timedelta(hours=3)
        posts =  models.Post.objects.filter(type__in=const.POST_TOPLEVEL, creation_date__lt=timestamp).exclude(type=const.POST_BLOG).order_by('-creation_date')
        return posts[:25]

    def item_title(self, item):
        if item.type != const.POST_QUESTION:
            return "%s: %s" % (item.get_type_display(), item.title)
        else:
            return item.title

    def item_description(self, item):
        #return item.content
        return item.html

    def item_guid(self, obj):
        return "http://%s%s" %(SITE.domain, obj.get_short_url())


class NotificationFeed(Feed):
    title = "NeuroStars notifications"
    link = "/"
    description = "Latest 25 notification for a given user"

    def title(self, obj):
        return " Notifications for %s" % obj.profile.display_name

    def get_object(self, request, uuid):
        obj = get_object_or_404(models.User, profile__uuid=uuid)
        return obj
        
    def items(self, obj):
        return models.Note.objects.filter(target=obj).select_related('sender', 'sender__profile').order_by('-date')[:25]

    def item_title(self, item):
        return item.content[:100]

    def item_description(self, item):
        return item.html

class PostBase(Feed):
    title = "NeuroStars Post Base"
    link = "/"
    description = "NeuroStars Post Base Class"

    def get_object(self, request, text):
        return text.split('+')[:10]
        
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.html
        #return item.content[:1000]

    #def item_extra_kwargs(self, item):
    #    return {'content_encoded': item.html}

    def item_guid(self, obj):
        return "http://%s%s" %(SITE.domain, obj.get_short_url())

class TagsFeed(PostBase):
    title = "NeuroStars Tags"
    link = "/"
    description = "NeuroStars - latest posts matching tags"

    def get_object(self, request, text):
        return text
        
    def title(self, obj):
        return "NeuroStars tags %s" % obj
 
    def items(self, obj):
        posts = models.query_by_tags(user=None, text=obj).order_by('-creation_date')
        return posts[:25]

class PostTypeFeed(PostBase):
    title = "Feed to a specific NeuroStars post type"
    link = "/"
    description = "NeuroStars - latest posts matching a post type"

    def get_object(self, request, text):
        # reverse mapping for quick lookups
        elems = text.split("+")
        codes = [ const.POST_REV_MAP.get(e, const.POST_QUESTION) for e in elems ]
        return (codes, text)
        
    def title(self, obj):
        codes, text = obj
        return "NeuroStars %s" % text
 
    def items(self, obj):
        codes, text = obj
        posts = models.Post.objects.filter(type__in=codes).order_by('-creation_date')
        return posts[:25]

class PostFeed(PostBase):
    title = "NeuroStars Post"
    link = "/"
    description = "NeuroStars post activity"

    def title(self, obj):
        return "NeuroStars activity on %s" % "+".join(obj)

    def items(self, obj):
        posts = models.Post.objects.filter(root__id__in=obj).order_by('-creation_date')
        return posts[:25]

class UserFeed(PostBase):
    def title(self, obj):
        return "NeuroStars user %s" % "+".join(obj)

    def items(self, obj):
        posts = models.Post.objects.filter(author__id__in=obj).order_by('-creation_date')
        return posts[:25]

class MyTagsFeed(PostBase):
    title = "NeuroStars MyTags"
    link = "/"
    description = "NeuroStars MyTags"

    def title(self, obj):
        return "NeuroStars my tags for %s" % obj.profile.display_name

    def get_object(self, request, uuid):
        obj = get_object_or_404(models.User, profile__uuid=uuid)
        return obj
        
    def items(self, obj):
        text  = obj.profile.my_tags
        posts = models.query_by_tags(user=obj, text=text).order_by('-creation_date')
        return posts[:15]
