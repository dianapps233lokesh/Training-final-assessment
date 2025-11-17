from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Q
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from activity_logs.utils import log_activity
from authentication.choices import UserType
from products.models import Category, Product
from products.serializers import CategorySerializer, ProductSerializer


class CategoryListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        log_activity(
            user=request.user,
            action="category_created",
            entity_type="category",
            entity_id=category.id,
            details=serializer.data,
            request=request,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Product.objects.all()

        # Filtering
        category_id = request.query_params.get("category")
        is_active = request.query_params.get("is_active")
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # Searching
        search_query = request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(category__name__icontains=search_query)
            )

        # Pagination
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)
        paginator = Paginator(queryset, page_size)

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(products, many=True)
        return Response(
            {
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "current_page": products.number,
                "results": serializer.data,
            }
        )

    def post(self, request):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        log_activity(
            user=request.user,
            action="product_created",
            entity_type="product",
            entity_id=product.id,
            details=serializer.data,
            request=request,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductRetrieveUpdateDestroyAPIView(APIView):
    permission_classes = [AllowAny]  # Public for GET, Admin for PUT/DELETE

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, id):
        product = self.get_object(id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, id):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        product = self.get_object(id)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        log_activity(
            user=request.user,
            action="product_updated",
            entity_type="product",
            entity_id=product.id,
            details=serializer.data,
            request=request,
        )
        return Response(serializer.data)

    def delete(self, request, id):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        product = self.get_object(id)
        product_data = ProductSerializer(product).data
        product.delete()
        log_activity(
            user=request.user,
            action="product_deleted",
            entity_type="product",
            entity_id=id,
            details=product_data,
            request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductSearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        search_query = request.query_params.get("q", "")
        if search_query:
            queryset = Product.objects.filter(
                Q(name__icontains=search_query)
                | Q(category__name__icontains=search_query)
            )
        else:
            queryset = Product.objects.all()

        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)
        paginator = Paginator(queryset, page_size)

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(products, many=True)
        return Response(
            {
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "current_page": products.number,
                "results": serializer.data,
            }
        )


class LowStockProductsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        queryset = Product.objects.filter(
            stock_quantity__lte=models.F("low_stock_threshold")
        )

        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)
        paginator = Paginator(queryset, page_size)

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(products, many=True)
        return Response(
            {
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "current_page": products.number,
                "results": serializer.data,
            }
        )
