import operator
from functools import reduce
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from users.permissions import IsAdminOrReadOnly, IsOwner, IsOwnerOrReadOnly
from .serializers import (ShoeColorSerializer, ShoeVariantDetailSerializer, 
ShoeVariantListSerializer, CartListSerializer, CategoryListSerializer, 
ModifyCartSerializer, RatingSerializer, ShoeDetailSerializer, ShoeFeatureSerializer, ShoeListSerializer,
 ShoeCategoryListSerializer, ShoeImageSerializer, ShoeSizeSerializer, 
 ParentCategoryListSerializer, ShoeCategorySerializer, ShoeSerializer)
from .models import (ShoeColor, ShoeVariant, CartItem, Category, Rating, Shoe, 
ShoeCategory, ShoeFeature, ShoeImage, ShoeSize)
from .utils import float_or_none


class ShoeListView(APIView):

    parser_classes = [JSONParser, MultiPartParser]
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, format=None):

        # splitting the categories into a list
        categories = request.GET.get("categories")
        search_query = request.GET.get("q")
        price_max = request.GET.get("price_max")
        price_min = request.GET.get("price_min")
        sizes = request.GET.get("sizes")
        ordering = request.GET.get("order")

        accepted_values = ["id", "id_desc", "price", "price_desc",
        "newest", "oldest"]

        if not ordering in accepted_values:
            ordering = "id"
        elif ordering.split("_")[-1] == "desc":
            ordering = "-" + ordering.split("_")[0]
        elif ordering == "newest":
            ordering = "date_restocked"
        elif ordering == "oldest":
            ordering = "-date_restocked"

        print(request.GET.get("test"))
        query = []

        # ------ QUERY BUILDING ------
        if  search_query:
            # search by name of shoe it's category
            query.append(Q(name__icontains= search_query) | Q(categories__category__name = search_query))

        if categories:
            categories = categories.split(",")
            clauses = (Q(categories__category__name=category) for category in categories)
            # for each category, return any shoe that has at least one category
            query.append(reduce(operator.or_,clauses))

        # getting the max price
        if float_or_none(price_max):
            price_max = float_or_none(price_max)
            query.append(Q(variants__price__lte=price_max))

        # getting the minimum price
        if float_or_none(price_min):
            price_min = float_or_none(price_min)
            query.append(Q(variants__price__gte=price_min))

        # getting the sizes to display
        if sizes:
            sizes = sizes.replace("-", " ")
            sizes = sizes.split(",")
            clauses = (Q(variants__size__name=size) for size in sizes)
            query.append(reduce(operator.or_, clauses))


        if len(query) > 0:
            query = reduce(operator.and_, query)
            if sizes and categories:
                shoes = Shoe.objects.all().prefetch_related('categories', 'variants').filter(query).order_by(ordering).distinct()
            elif sizes or price_max or price_min:
                shoes = Shoe.objects.all().prefetch_related( 'variants').filter(query).order_by(ordering).distinct()
            elif categories or search_query:
                shoes = Shoe.objects.all().prefetch_related('categories').filter(query).order_by(ordering).distinct()
            else:
                shoes = Shoe.objects.all().filter(query).distinct()
            
        else:
            shoes = Shoe.objects.all().order_by(ordering).distinct()

        serializer = ShoeListSerializer(shoes, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ShoeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("valid")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ShoeDetailView(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, id, format=None):
        shoe = get_object_or_404(Shoe, id=id)
        serializer = ShoeDetailSerializer(shoe)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        shoe = get_object_or_404(Shoe, id=id)
        serializer = ShoeSerializer(shoe, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        shoe = get_object_or_404(Shoe, id=id)
        shoe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ShoeFeatureListCreateView(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, shoe_id, format = None):
        features = ShoeFeature.objects.filter(shoe__id = shoe_id)
        serializer = ShoeFeatureSerializer(features, many = True)
        return Response(serializer.data)

    def post(self, request , shoe_id, format = None):
        for item in request.data:
            item["shoe"] = shoe_id
        serializer = ShoeFeatureSerializer(data = request.data, many = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShoeFeatureUpdateDeleteView(APIView):

    permission_classes = [IsAdminUser]

    def get_object(self, shoe_id, feature_id):
        obj  = get_object_or_404(ShoeFeature, shoe__id = shoe_id, id = feature_id)
        return obj

    def put(self, request , shoe_id, feature_id, format = None):
        request.data["shoe"] = shoe_id
        feature = self.get_object(shoe_id, feature_id)
        serializer = ShoeFeatureSerializer(feature, data = request.data, partial = True)
        if serializer.is_valid():

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, shoe_id, feature_id, format = None):

        feature = self.get_object(shoe_id, feature_id)
        feature.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class ShoeImageListView(APIView):

    parser_classes = [JSONParser, MultiPartParser]
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, format=None):
        shoe_images = ShoeImage.objects.all()
        serializer = ShoeImageSerializer(shoe_images, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ShoeImageSerializer(data=request.data, context={"request" : request})
        if request.FILES.get("image"):
            image = request.FILES.get("image")
            request.FILES["medium"] = image
            request.FILES["thumbnail"] = image
            request.data["medium"] = request.FILES["medium"]
            request.data["thumbnail"] = request.FILES["thumbnail"]

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class ShoeImageDetailView(APIView):

    parser_classes = [JSONParser, MultiPartParser]
    permission_classes = [IsAdminUser]

    def get_object(self, image_id):
        obj = get_object_or_404(ShoeImage, id = image_id)
        return obj

    def put(self, request, image_id,  format=None):
        shoe_image = self.get_object( image_id)
        serializer = ShoeImageSerializer(shoe_image, data=request.data, context={'request' : request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, image_id,  format=None):
        shoe_image = self.get_object( image_id)
        shoe_image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoeSizeView(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get (self, request, format=None):
        shoe_sizes = ShoeSize.objects.all()
        serializer = ShoeSizeSerializer(shoe_sizes, many=True)
        return Response(serializer.data)

    def post (self, request, format=None):
        serializer = ShoeSizeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShoeSizeUpdateDeleteView(APIView):

    permission_classes = [IsAdminUser]

    def get_object(self, size_id):
        obj = get_object_or_404(ShoeSize, id = size_id)
        return obj

    def put(self, request, size_id, format = None):
        shoe_size = self.get_object(size_id)
        serializer = ShoeSizeSerializer(shoe_size, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, size_id, format = None):
        shoe_size = self.get_object(size_id)
        shoe_size.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class ShoeColorListCreateView(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, shoe_id):
        obj = get_object_or_404(ShoeColor, shoe_id = shoe_id)
        return obj

    def get(self, request, shoe_id, format=None):
        colors = ShoeColor.objects.filter(shoe__id = shoe_id)
        serializer = ShoeColorSerializer(colors, many=True)
        return Response(serializer.data)

    def post(self, request, shoe_id, format=None):
        if type(request.data) == dict:
            request.data["shoe"] = shoe_id
        serializer = ShoeColorSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ShoeColorUpdateDeleteView(APIView):

    permission_classes = [IsAdminUser]

    def get_object(self, color_id):
        obj = get_object_or_404(ShoeColor, id = color_id)
        return obj

    def put(self, request, color_id, format = None):
        shoe_size = self.get_object(color_id)
        serializer = ShoeColorSerializer(shoe_size, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, color_id, format = None):
        shoe_size = self.get_object(color_id)
        shoe_size.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class ShoeVariantListView(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, shoe_id, format=None):
        available_shoe_sizes = ShoeVariant.objects.filter(shoe__id = shoe_id)
        serializer = ShoeVariantListSerializer(available_shoe_sizes, many=True)
        return Response(serializer.data)

    def post(self, request, shoe_id, format=None):
        if type(request.data) == dict:
            request.data["shoe"] = shoe_id
            try:
                shoe_size = ShoeSize.objects.get(name=request.data['size'])
            except :
                request.data['size'] = None
            else:
                request.data['size'] = shoe_size.id
            
        serializer = ShoeVariantDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return_serializer = ShoeVariantListSerializer(ShoeVariant.objects.get(id = serializer.data["id"]))
            return Response(return_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShoeVariantDetailView(APIView):

    permission_classes = [IsAdminUser]

    def get_object(self, variant_id, shoe_id):
        obj = get_object_or_404(ShoeVariant, id = variant_id, shoe__id = shoe_id)
        return obj

    def put(self, request, shoe_id, variant_id, format=None):
        shoe_size = self.get_object(variant_id, shoe_id)
        serializer = ShoeVariantDetailSerializer(shoe_size, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return_serializer = ShoeVariantListSerializer(ShoeVariant.objects.get(id = serializer.data["id"]))
            return Response(return_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, shoe_id, variant_id, format=None):
        shoe_size = self.get_object(variant_id, shoe_id)
        shoe_size.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryListView(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, format=None):
        categories = Category.objects.filter(parent_id = None)
        serializer = ParentCategoryListSerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CategoryListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class CategoryDetailView(APIView):

    permission_classes = [IsAdminOrReadOnly]
    
    def get(self, request, category_id, format=None):
        category = get_object_or_404(Category, id = category_id)
        serializer = CategoryListSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, category_id, format = None):
        category = get_object_or_404(Category, id = category_id)
        serializer = CategoryListSerializer(category, request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, category_id, format=None):
        category = get_object_or_404(Category, id = category_id)
        category.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class ShoeCategoryView(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, shoe_id, format=None):
        shoe_categories = ShoeCategory.objects.filter(shoe__id = shoe_id)
        serializer = ShoeCategoryListSerializer(shoe_categories, many=True)
        return Response(serializer.data)

    def post(self, request, shoe_id, format=None):
        request.data["shoe"] = shoe_id if type(request.data) == dict else None
        serializer = ShoeCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class ShoeCategoryUpdateDeleteView(APIView):

    permission_classes = [IsAdminOrReadOnly]
    
    def get_object(self, category_id, shoe_id):
        obj = get_object_or_404(ShoeCategory, id = category_id, shoe__id = shoe_id)
        return obj

    def put(self, request, category_id, shoe_id, format = None):
        category = self.get_object(category_id, shoe_id)
        serializer = ShoeCategorySerializer(category, request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, category_id, shoe_id, format=None):
        category = self.get_object(category_id, shoe_id)
        category.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


class UserCartView(APIView):

    def get(self, request, user_id, format=None):

        # if the current user isn't the owner of the cart being viewed
        if not user_id == request.user.id:
            return Response({"detail" :"You do not have permission to access another user's cart"}, status=status.HTTP_403_FORBIDDEN)

        # get all cart items
        cart_items = CartItem.objects.filter(user__id = user_id, quantity__gt  = 0).order_by('-modified_at')
        serializer = CartListSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request, user_id, format=None):

        # if the current user isn't the owner of the cart being viewed
        if not user_id == request.user.id:
            return Response({"detail" :"You do not have permission to access another user's cart"}, status=status.HTTP_403_FORBIDDEN)
        
        # trying to fetch the cart item incase there's a duplicate
        # so that the quantity would be incremented rather than having
        # multiple cart items of the same item
        try:
            cart_item = CartItem.objects.get(shoe__id = request.data['shoe'], user__id = user_id)
        except:
            serializer = ModifyCartSerializer(data=request.data)
        else:
            if 'quantity' in request.data:
                request.data['quantity']+= cart_item.quantity
            serializer = ModifyCartSerializer(cart_item, data=request.data)

        request.data['user'] = user_id
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class UserCartUpdateDeleteView(APIView):

    permission_classes = [IsOwner]

    def get_object(self, cart_item_id):
        obj = get_object_or_404(CartItem, id = cart_item_id, user = self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj

    def put(self, request, cart_item_id, format = None):
        cart_item = self.get_object(cart_item_id)
        serializer = ModifyCartSerializer(cart_item, request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, cart_item_id, format=None):
        cart_item = self.get_object(cart_item_id)
        cart_item.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


class ShoeRatingView(APIView):


    def get(self, request, shoe_id, format = None):
        ratings = Rating.objects.filter(shoe__id = shoe_id)
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)

    def post(self, request, shoe_id, format = None):
        user = request.user

        # getting the user making the review 
        request.data["user"] = user.id

        # getting the shoe being reviewed
        request.data["shoe"] = shoe_id

        # making sure one user can't leave two reviews on one product
        try:
            user_rating = Rating.objects.get(user = user, shoe__id = shoe_id)
        except:
            serializer = RatingSerializer(data = request.data)
        else:
            serializer = RatingSerializer(user_rating , data = request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, shoe_id, format = None):

        # delete the rating by the user making the request if any, 
        #  else return a 404 error.
        try:
            rating = Rating.objects.get(shoe__id = shoe_id, user = request.user)
        except:
            return Response({ "detail" :"Rating not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            rating.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
