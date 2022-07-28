from rest_framework import serializers
from shoes.models import AvailableShoeSize

class ProductListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required = True)
    quantity = serializers.IntegerField(required = True)
    price = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    
    class Meta:
        fields = ["id", "quantity", "price", "name", "discount"]

    def validate(self, data):
        try:
            item = AvailableShoeSize.objects.get(id = data["id"])
        except:
            raise serializers.ValidationError("Product selected doesn't exist")
        else:
            if item.quantity < data["quantity"]:
                raise serializers.ValidationError({"quantity" : f"Items more than available items. there are {item.quantity} items available"})
        return data

    def get_price(self, obj):
        item = AvailableShoeSize.objects.get(id = obj["id"])
        return item.price

    def get_name(self, obj):
        item = AvailableShoeSize.objects.get(id = obj["id"])
        return f"{item.shoe.name} - {item.shoe_size.name}"

    def get_discount (self, obj):
        item =  AvailableShoeSize.objects.get(id = obj["id"])
        return item.discount


PRODUCT_SOURCE_CHOICES = [
    (1, "Cart"),
    (2, "Buy now")
]

class ProductCheckoutSerializer(serializers.Serializer):
    product_source = serializers.ChoiceField(required = True, choices=PRODUCT_SOURCE_CHOICES)
    products = ProductListSerializer(many=True, required=False)

    class Meta:
        fields = "__all__"
    
    def validate(self, data):
        if data["product_source"] == 2:
            if not "products" in data:
                raise serializers.ValidationError({"products" : "This field is required"})
        
        elif data["product_source"] == 1:
            if not "products" in data:
                raise serializers.ValidationError({"products" : "Cart is empty"})
        return data