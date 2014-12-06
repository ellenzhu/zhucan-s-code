from django.db import models

class BlogPost(models.Model):
  title = models.CharField(max_length=200)
  text_body = models.TextField()
  published = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return "{0} ({1}-{2}-{3})".format(self.title, 
      self.published.year, 
      self.published.month, 
      self.published.day)

class Comment(models.Model):
  comment = models.TextField()
  post = models.ForeignKey(BlogPost)



