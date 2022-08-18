from datetime import datetime
from decimal import Decimal
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from users.models import User
from django.utils.translation import gettext_lazy as _
from PIL import Image

# each shoe 
class Shoe(models.Model):
    id = models.AutoField(primary_key=True, blank=False, auto_created=True)
    name = models.CharField (null=False,blank=False,max_length=50) 
    description = models.TextField( blank=True, null=True)
    display = models.BooleanField(default=False, null=False)
    date_added = models.DateTimeField(auto_now_add=True, null=False)
    date_restocked = models.DateTimeField(null=False, blank=True, default=datetime.now())

    class Meta:
        db_table = "shoe"

    def __str__(self):
        return self.name

class ShoeFeature(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True, null=False)
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name="features")
    feature = models.CharField(max_length = 255, null=False, blank=False)

# the standard shoe sizes that every sheo can be classified into
class ShoeSize(models.Model):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    name = models.CharField(max_length=10, null=False, blank=False, unique=True)

    class Meta:
        db_table = "shoe_size"

    def __str__(self):
        return self.name

# the various colors available to a shoe
class ShoeColor(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False, blank=False)
    name = models.CharField(max_length=50, null=False, blank=False, default="default")
    hex_code = models.CharField(max_length=6, null=True, blank=True)
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name = "colors")

    class Meta:
        db_table = "shoe_color"
        unique_together  = ["name", "shoe"]

    def __str__(self):
        return f"{self.shoe.name} - {self.name}"

# the images for each shoe
class ShoeImage(models.Model):
    id = models.AutoField(primary_key=True, blank=False, auto_created=True, null=False)
    image = models.ImageField (null=False, blank=False, upload_to="shoe_images",validators=[FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg", "webp"])])
    medium = models.ImageField(upload_to="shoe_images/medium", validators=[FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg", "webp"])])
    thumbnail = models.ImageField(upload_to="shoe_images/thumbnail", validators=[FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg", "webp"])])
    color = models.ForeignKey(ShoeColor, on_delete=models.CASCADE, related_name='images')

    class Meta:
        db_table = "shoe_image"
        unique_together = ["image", "color"]

    def save(self, *args, **kwargs):
        super().save()
        thumbnail = Image.open(self.thumbnail.path)
        medium = Image.open(self.medium.path)

        if thumbnail.width > 128 or thumbnail.height > 128:
            thumbnail_size = (128, int(128 * thumbnail.height / thumbnail.width)) if thumbnail.width <= thumbnail.height else (int(128 * thumbnail.width / thumbnail.height), 128)
            thumbnail = thumbnail.resize(thumbnail_size)
            thumbnail.save(self.thumbnail.path)

        if medium.width > 300 or medium.height > 300:
            medium_size = (300, int(300 * medium.height / medium.width)) if medium.width <= medium.height else (int(300 * medium.width / medium.height), 300)
            medium = medium.resize(medium_size)
            medium.save(self.medium.path)

# shoe variants
class ShoeVariant(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False, blank=False)
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name="variants")
    size = models.ForeignKey(ShoeSize, on_delete=models.CASCADE, related_name="shoes")
    color = models.ForeignKey(ShoeColor, on_delete=models.CASCADE, related_name="shoes")
    quantity = models.PositiveSmallIntegerField ( null= False, default=0)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=False)
    discount = models.DecimalField(max_digits=4, decimal_places=1, default= Decimal('0.00'))

    class Meta:
        db_table = "shoe_variant"
        unique_together = ['shoe', 'size', 'color']

    def __str__(self):
        return f"{self.shoe.name} color:{self.color.name} size:{self.size.name}"


# each actegory like the category of gender, season
class Category(models.Model):
    id = models.SmallAutoField(primary_key=True, blank=False, null=False)
    name = models.CharField(max_length=30, null=False, blank=False, unique=True)
    special = models.BooleanField(null=False, default=False)
    image = models.ImageField (null=True, blank=True, upload_to="shoe_images",validators=[FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg", "webp"])])
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name="children" )

    class Meta:
        db_table = "category"
        unique_together = ["parent", "name"]

    def __str__(self):
        return f"{self.name}"

# the category each shoe falls under
class ShoeCategory(models.Model):
    id = models.AutoField(primary_key=True,blank=False, null=False, auto_created=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='shoes')
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        db_table = "shoe_category"
        verbose_name_plural = "shoe categories"
        unique_together = ["category", "shoe"]

    def __str__(self):
        return f"{self.shoe.name} - {self.category.name}"

    def clean(self):
        if self.category.id < 2:
            raise ValidationError(_("Please select a Valid category"))
        if self.category.parent_id != 1:
            raise ValidationError(_("Please select a category, not a category group"))

# the user's shopping cart 
class CartItem(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    user = models.ForeignKey(User, related_name='shopping_cart', null=False, blank=False, on_delete=models.CASCADE)
    shoe = models.ForeignKey(ShoeVariant, related_name='in_cart', null=False, blank=False, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(null=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

# ratings and reviews left by the user
class Rating(models.Model):
    id = models.AutoField(primary_key=True, null=False, auto_created=True)
    STAR_CHOICES = [
        (1, "1 star"),
        (2, "2 stars"),
        (3, "3 stars"),
        (4, "4 stars"),
        (5, "5 stars"),
    ]
    stars = models.PositiveSmallIntegerField(choices=STAR_CHOICES, null=False, blank=False)
    feedback = models.TextField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE)

    class Meta:
        db_table = "rating"
        unique_together = ["user", "shoe"]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.stars} star(s)"