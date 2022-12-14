import operator
import string
from functools import reduce
from django.core.exceptions import ValidationError
from django.db.models import Q, Max, Min, Avg
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from payments.models import Purchase
from users.models import User
from .validators import validate_file_extension
from .models import (CartItem, Category, Rating, Shoe, ShoeCategory, ShoeFeature, ShoeImage, 
ShoeSize, ShoeVariant, ShoeColor)


class ShoeImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoeImage
        fields = "__all__"
    

class ShoeColorSerializer(serializers.ModelSerializer):
    images = ShoeImageSerializer(many=True, read_only=True)

    class Meta:
        model = ShoeColor
        fields = "__all__"

    def validate_hex_code(self, value):
        for letter in value.upper():
            if not letter in string.hexdigits:
                raise serializers.ValidationError("Invalid hex code")
        if not len(value) == 6:
            raise serializers.ValidationError("Invalid hex code. Hex code must be 6 digits e.g FFFFFF")
        return value.upper()
            


class ShoeColorVariantSerializer(serializers.ModelSerializer):
    images = ShoeImageSerializer(many=True, read_only=True)

    class Meta:
        model = ShoeColor
        fields = "__all__"

class ShoeVariantListSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField("get_shoe_size_name")
    color = ShoeColorVariantSerializer(read_only=True)
    
    class Meta:
        model = ShoeVariant
        fields = "__all__"

    def get_shoe_size_name(self, obj):
        return obj.size.name

class ShoeVariantDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoeVariant
        fields = "__all__"
        extra_kwargs = {"size": {"error_messages": {"null": "Enter a valid shoe size"}}}

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Category

class ParentCategoryListSerializer(serializers.ModelSerializer):
    children = CategoryListSerializer(many=True, read_only=True)

    class Meta:
        fields = ["id", "name", "special", "image", "children"]
        model = Category

class ShoeCategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = "__all__"
        model = ShoeCategory

    def validate_category(self, value):
        if not value.parent:
            raise serializers.ValidationError("Cannot chose a parent category for an item")

        return value

class ShoeCategoryListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField("get_category_name")
    shoe = serializers.SerializerMethodField("get_shoe_name")
    
    class Meta:
        fields = ["id", "shoe", "category"]
        model = ShoeCategory
    
    def get_category_name(self, obj):
        return obj.category.name

    def get_shoe_name(self, obj):
        return obj.shoe.name

class ShoeFeatureSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = "__all__"
        model = ShoeFeature

class ShoeListSerializer(serializers.ModelSerializer):
    images = ShoeImageSerializer(many=True, read_only=True)
    quantity = serializers.SerializerMethodField("get_quantity")
    price_min = serializers.SerializerMethodField("get_min_price")
    price_max = serializers.SerializerMethodField("get_max_price")
    price_avg = serializers.SerializerMethodField("get_avg_price")
    ratings = serializers.SerializerMethodField("get_ratings")
    images = serializers.SerializerMethodField()

    class Meta:
        model = Shoe
        fields = ["id", "name","date_restocked", "images", "quantity", "price_min", "price_max", "price_avg", "ratings"]

    def get_quantity(self, obj):
        available_sizes = ShoeVariant.objects.filter(shoe=obj)
        qty = 0
        for item in available_sizes:
            qty+=item.quantity
        return qty

    def get_min_price(self, obj):
        return ShoeVariant.objects.filter(shoe=obj).aggregate(Min('price'))["price__min"]

    def get_max_price(self, obj):
        return ShoeVariant.objects.filter(shoe=obj).aggregate(Max('price'))["price__max"]

    def get_avg_price(self, obj):
        return ShoeVariant.objects.filter(shoe=obj).aggregate(Avg('price'))["price__avg"]

    def get_ratings(self, obj):
        ratings = Rating.objects.filter(shoe = obj)
        count = ratings.count()
        stars = 0
        if count > 0:
            for rating in ratings:
                stars+= rating.stars
            stars = stars/count
        return {"stars" : stars, "count" : count}

    def get_images(self, obj):
        color = None
        try:
            color = ShoeColor.objects.get(name = "default")
        except:
            try:
                color = ShoeColor.objects.filter().first()
            except:
                pass
        if color:
            return ShoeImageSerializer(color.images.first()).data



class ShoeDetailSerializer(serializers.ModelSerializer):
    features = ShoeFeatureSerializer(many = True, read_only = False,required = False)
    categories = ShoeCategoryListSerializer(many=True, read_only=False, required=False)
    ratings = serializers.SerializerMethodField()

    class Meta:
        model = Shoe
        fields = "__all__"
        depth = 1

    def get_ratings(self, obj):
        ratings = Rating.objects.filter(shoe = obj)
        count = ratings.count()
        stars = 0
        if count > 0:
            for rating in ratings:
                stars+= rating.stars
            stars = stars/count
        return {"stars" : stars, "count" : count}

class ShoeSerializer(serializers.ModelSerializer):
    features = ShoeFeatureSerializer(many = True, read_only = False, required = False)
    categories = ShoeCategoryListSerializer(many=True, read_only=False, required=False)
    class Meta:
        model = Shoe
        fields = "__all__"
        read_only_fields = ["date_restocked", "date_added"]

class ShoeSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoeSize
        fields = "__all__"

class CartListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ["id", "quantity", "shoe"]
        depth = 2

class ModifyCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = "__all__"

    def validate_quantity(self, value):
        quantity = ShoeVariant.objects.get(id = self.initial_data['shoe']).quantity
        if quantity < value:
            raise ValidationError(f"Items more than available items. there are {quantity} items available")
        return value


class UserCartSerializer(serializers.ModelSerializer):
    cart = CartListSerializer(many=True)

    class Meta:
        model = User
        fields = ["cart"]
    

class RatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = "__all__"

    def validate(self, data):
        shoes = Purchase.objects.filter(shoe__shoe = data["shoe"], transaction__user = data["user"])
        if len(shoes) < 1:
            raise ValidationError({"user" : "You must purchase this product in order to leave a rating or review"})
        return data