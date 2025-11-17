from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from activity_logs.models import ActivityLog
from activity_logs.serializers import ActivityLogSerializer
from authentication.choices import UserType


class ActivityLogListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only admin can list logs

    def get(self, request):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        queryset = ActivityLog.objects.all()

        # Filtering
        user_id = request.query_params.get("user_id")
        action = request.query_params.get("action")
        entity_type = request.query_params.get("entity_type")
        entity_id = request.query_params.get("entity_id")

        if user_id:
            queryset = queryset.filter(user__id=user_id)
        if action:
            queryset = queryset.filter(action__icontains=action)
        if entity_type:
            queryset = queryset.filter(entity_type__icontains=entity_type)
        if entity_id:
            queryset = queryset.filter(entity_id__icontains=entity_id)

        # Pagination
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)
        paginator = Paginator(queryset, page_size)

        try:
            logs = paginator.page(page)
        except PageNotAnInteger:
            logs = paginator.page(1)
        except EmptyPage:
            logs = paginator.page(paginator.num_pages)

        serializer = ActivityLogSerializer(logs, many=True)
        return Response(
            {
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "current_page": logs.number,
                "results": serializer.data,
            }
        )

    def post(self, request):
        # Internal use, so no permission check here, but ensure data integrity

        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ActivityLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Set user and username from request if available
        if request.user and request.user.is_authenticated:
            serializer.validated_data["user"] = request.user
            serializer.validated_data["username"] = request.user.username
        else:
            serializer.validated_data["user"] = None
            serializer.validated_data["username"] = "Anonymous"

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserActivityLogListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = ActivityLog.objects.filter(user__id=user_id)

        # Pagination
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)
        paginator = Paginator(queryset, page_size)

        try:
            logs = paginator.page(page)
        except PageNotAnInteger:
            logs = paginator.page(1)
        except EmptyPage:
            logs = paginator.page(paginator.num_pages)

        serializer = ActivityLogSerializer(logs, many=True)
        return Response(
            {
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "current_page": logs.number,
                "results": serializer.data,
            }
        )
