from rest_framework import serializers


class TrendParamsSerializer(serializers.Serializer):
    date = serializers.CharField(required=True)
    value = serializers.CharField(required=False)
    freq = serializers.ChoiceField(choices=["D", "W", "M"], default="D")
    agg = serializers.ChoiceField(choices=["sum", "mean", "count"], default="sum")


class RowsParamsSerializer(serializers.Serializer):
    columns = serializers.CharField(required=False)
    sort = serializers.CharField(required=False)
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=50)


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files allowed")
        return value

