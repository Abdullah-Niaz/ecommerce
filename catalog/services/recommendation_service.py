import itertools
import json
from collections import Counter
from django.conf import settings
from django.db import transaction
from catalog.models import Order, Product, ProductRecommendation
import redis

REDIS = redis.StrictRedis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))

class RecommendationService:
    COOC_KEY = "rec:cooccurrence"            # hash of "p1:p2" -> count
    TOP_N = 10

    @staticmethod
    def _pair_key(a_id, b_id):
        return f"{min(a_id,b_id)}:{max(a_id,b_id)}"

    @classmethod
    def increment_cooccurrence_for_order(cls, order: Order):
        if not order:
            return
        product_ids = list(order.items.values_list('product_id', flat=True))
        if len(product_ids) < 2:
            return
        pipe = REDIS.pipeline()
        for a, b in itertools.combinations(product_ids, 2):
            key = cls._pair_key(a, b)
            pipe.hincrby(cls.COOC_KEY, key, 1)
        pipe.execute()
        # Optionally update ProductRecommendation for each product
        cls._refresh_product_recommendations(product_ids)

    @classmethod
    def _refresh_product_recommendations(cls, product_ids):
        # For each product, gather top co-occurring partners from Redis and persist top N
        for pid in set(product_ids):
            raw = REDIS.hgetall(cls.COOC_KEY)
            counts = {}
            for k_bytes, v_bytes in raw.items():
                k = k_bytes.decode()
                v = int(v_bytes.decode())
                a,b = k.split(':')
                a, b = int(a), int(b)
                if pid == a:
                    counts[b] = counts.get(b,0)+v
                elif pid == b:
                    counts[a] = counts.get(a,0)+v
            top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:cls.TOP_N]
            # Persist to ProductRecommendation
            with transaction.atomic():
                # simple replace strategy
                ProductRecommendation.objects.filter(product_id=pid).delete()
                bulk = []
                for rec_pid, score in top:
                    bulk.append(ProductRecommendation(product_id=pid, recommended_product_id=rec_pid, score=score))
                ProductRecommendation.objects.bulk_create(bulk)
            # Cache top list in Redis for quick endpoint hits
            cache_key = f"rec:product:{pid}:top"
            REDIS.set(cache_key, json.dumps([{"id": r[0], "score": r[1]} for r in top]), ex=24*3600)

    @classmethod
    def get_recommendations_for_product(cls, product_id, limit=10):
        cache_key = f"rec:product:{product_id}:top"
        payload = REDIS.get(cache_key)
        if payload:
            return json.loads(payload)
        # fallback to DB
        qs = ProductRecommendation.objects.filter(product_id=product_id).order_by('-score')[:limit]
        return [{"id": r.recommended_product_id, "score": r.score} for r in qs]
