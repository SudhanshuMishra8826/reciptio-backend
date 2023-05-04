"""
Recepie serializers
"""
from rest_framework import serializers
from core.models import Recepie, Tag


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for tag objects
    """

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipieSerializer(serializers.ModelSerializer):
    """
    Serializer for recepie objects
    """
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recepie
        fields = ('id', 'title', 'price',
                  'time_minutes', 'link', 'tags')
        read_only_fields = ('id',)

    def _get_or_create_tag(self, tags, recepie):
        """
        Get or create a tag
        """
        for tag in tags:
            tag_obj = Tag.objects.get_or_create(user=self
                                                .context['request'].user,
                                                **tag)
            recepie.tags.add(tag_obj[0])

    def create(self, validated_data):
        """
        Create a new recepie
        """
        tags = validated_data.pop('tags', [])
        recepie = Recepie.objects.create(**validated_data)
        self._get_or_create_tag(tags, recepie)
        return recepie

    def update(self, instance, validated_data):
        """
        Update a recepie
        """
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tag(tags, instance)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class RecepieDetailSerializer(RecipieSerializer):
    """
    Serializer for recepie detail
    """
    class Meta(RecipieSerializer.Meta):
        fields = RecipieSerializer.Meta.fields + ('description',)
