from rest_framework import serializers

from .models import (
    Film, FilmGenre, Installation,
    Performance, InstallationGenre
)


class InstallationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Installation
        exclude = ('polymorphic_ctype',)


class FilmSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Film
        exclude = ('polymorphic_ctype',)


class PerformanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Performance
        exclude = ('polymorphic_ctype',)


class FilmGenreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FilmGenre


class InstallationGenreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InstallationGenre

