from rest_framework.response import Response
from rest_framework import serializers, status


def view_validation(serializer: serializers.ModelSerializer) -> Response:
    """
    Оформленный вывод результата проверки валидности сериализатора
    """
    if serializer.is_valid():
        serializer.save()
        return Response({"status": str(status.HTTP_200_OK), "detail": serializer.data}, status=status.HTTP_200_OK)
    return Response(
        {"status": str(status.HTTP_400_BAD_REQUEST), "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
    )


def calculate_view_validation(serializer: serializers.Serializer) -> Response:
    """
    Оформленный вывод результата проверки валидности сериализатора
    """
    if serializer.is_valid(raise_exception=True):
        return Response({"status": str(status.HTTP_200_OK), "detail": serializer.data}, status=status.HTTP_200_OK)
    return Response(
        {"status": str(status.HTTP_400_BAD_REQUEST), "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
    )
