"""
Views for recipe APIs.
"""
from drf_spectacular.utils import(
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes
)

from rest_framework import (
    viewsets,
    mixins,
    )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
    Ingredient,
    )
from recipe import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter('tags', OpenApiTypes.STR, description='Comma seperated list of Tag IDs to filter',),
            OpenApiParameter('ingredients', OpenApiTypes.STR, description='Comma separated list of ingredient IDs to filter'),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View doe manage recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _param_to_ints(self, qs):
        """Convert a list string to intergers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        # return self.queryset.filter(user=self.request.user).order_by('-id')
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._param_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._param_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id_in=ingredient_ids)

        return queryset.filter(user=self.request.user).order_by('-id').distinct()


    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create new recipe."""
        serializer.save(user=self.request.user)

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter('assigned_only', OpenApiTypes.INT, enum=[0,1], description='Filter by items assigned to recipes.')
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                mixins.UpdateModelMixin,
                mixins.ListModelMixin,
                viewsets.GenericViewSet):
        """Base viewset for recipe attribute"""
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

        def get_queryset(self):
            """Filter queryset to authenticated user."""
            assigned_only = bool(
                int(self.request.query_params.get('assigned_only', 0))
            )
            queryset = self.queryset
            if assigned_only:
                queryset = queryset.filter(recipe__isnull=False)
            return self.queryset.filter(user=self.request.user).order_by('-name').distinct()


class TagViewSet(BaseRecipeAttrViewSet):
    """manage Tag in DB."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()




