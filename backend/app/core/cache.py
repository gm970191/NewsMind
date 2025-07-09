"""
缓存管理模块
"""
import time
import json
from typing import Any, Optional, Dict
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """简单内存缓存"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self._cache:
            item = self._cache[key]
            if time.time() < item['expires_at']:
                return item['value']
            else:
                # 过期，删除
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """设置缓存值"""
        self._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl
        }
    
    def delete(self, key: str) -> None:
        """删除缓存值"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        current_time = time.time()
        active_items = sum(1 for item in self._cache.values() if current_time < item['expires_at'])
        expired_items = len(self._cache) - active_items
        
        return {
            'total_items': len(self._cache),
            'active_items': active_items,
            'expired_items': expired_items,
            'memory_usage': len(json.dumps(self._cache))
        }


# 全局缓存实例
cache = SimpleCache()


def cached(ttl: int = 300, key_prefix: str = ""):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {cache_key}, cached for {ttl}s")
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str = None):
    """缓存失效装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # 清除相关缓存
            if pattern:
                # 这里可以实现模式匹配的缓存清除
                # 目前简单实现：清除所有缓存
                cache.clear()
                logger.debug(f"Cache invalidated for pattern: {pattern}")
            
            return result
        return wrapper
    return decorator 