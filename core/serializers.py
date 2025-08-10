from rest_framework import serializers

class TrendParamsSerializer(serializers.Serializer):
    date = serializers.CharField(required=True)
    value = serializers.CharField(required=False, allow_blank=True)
    freq = serializers.ChoiceField(choices=["D","W","M"], default="D")
    agg = serializers.ChoiceField(choices=["sum","mean","count"], default="sum")

class RowsParamsSerializer(serializers.Serializer):
    columns = serializers.CharField(required=False, allow_blank=True)
    sort = serializers.CharField(required=False, allow_blank=True)
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=50)