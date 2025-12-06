from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from catalog.models import Product
from .serializers import ProductSerializer
from catalog.services.recommendation_service import RecommendationService

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'

    @action(detail=True, methods=['get'], url_path='recommended')
    def recommended(self, request, id=None):
        limit = int(request.query_params.get('limit', 10))
        recs = RecommendationService.get_recommendations_for_product(int(id), limit=limit)
        # fetch product details for these ids
        prod_ids = [r['id'] for r in recs]
        prods = Product.objects.filter(id__in=prod_ids)
        prod_map = {p.id: p for p in prods}
        results = []
        for r in recs:
            p = prod_map.get(r['id'])
            if not p:
                continue
            results.append({
                "id": p.id,
                "title": p.title,
                "score": r.get('score', 0)
            })
        return Response({"product_id": int(id), "recommended": results})

    @action(detail=False, methods=['get'], url_path='trending')
    def trending(self, request):
        # simple placeholder. In prod compute and cache separately.
        from django.core.cache import cache
        cache_key = "products:trending:top20"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        # fallback: most purchased in last 7 days using PurchaseLog - simple count
        from catalog.models import PurchaseLog
        from django.utils import timezone
        from datetime import timedelta
        since = timezone.now() - timedelta(days=7)
        qs = PurchaseLog.objects.filter(timestamp__gte=since).values('product').annotate(count=models.Count('id')).order_by('-count')[:20]
        prod_ids = [q['product'] for q in qs]
        prods = Product.objects.filter(id__in=prod_ids)
        serializer = ProductSerializer(prods, many=True)
        data = serializer.data
        cache.set(cache_key, data, 60*60)  # 1 hour TTL
        return Response(data)
