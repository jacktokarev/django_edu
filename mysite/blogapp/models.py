from django.db import models
from django.urls import reverse

# Create your models here.


class Author(models.Model):

    class Meta:
        verbose_name = "Author"

    name = models.CharField(max_length=100, db_index=True, verbose_name="Name")
    bio = models.TextField(blank=True, verbose_name="Biography")

    def __str__(self) -> str:
        return f"{self._meta.verbose_name}_{self.pk}, {self.name}"


class Category(models.Model):

    class Meta:
        verbose_name = "Category"

    name = models.CharField(max_length=40, verbose_name="Category")

    def __str__(self) -> str:
        return f"{self._meta.verbose_name}_{self.pk}, {self.name}"


class Tag(models.Model):

    class Meta:
        verbose_name = "Tag"

    name = models.CharField(max_length=20, verbose_name="Tag")

    def __str__(self) -> str:
        return f"{self._meta.verbose_name}_{self.pk}, {self.name}"


class Article(models.Model):

    class Meta:
        verbose_name = "Article"

    title = models.CharField(max_length=200, verbose_name="Title")
    content = models.TextField(blank=False, verbose_name="Content")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="")
    author = models.ForeignKey(Author, on_delete=models.CASCADE,db_index=True, verbose_name="Author")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_index=True, verbose_name="Category")
    tags = models.ManyToManyField(Tag, related_name="articles", verbose_name="Tags")

    def __str__(self) -> str:
        return f"{self._meta.verbose_name}_{self.pk}, {self.title}"

    def get_absolute_url(self):
        return reverse("blogapp:article-details", kwargs={"pk": self.pk})
    
