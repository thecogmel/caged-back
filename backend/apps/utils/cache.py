import hashlib
import logging
import environ

from functools import wraps

from django.db import models
from django.core.cache import cache
from django.db.models.signals import post_save
from django.db.models.signals import post_delete

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

def cache_method(timeout=10):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            env = environ.Env()
            if env.bool("BACKEND_CACHE_ENABLE") == True:
                key = (func.__name__, args, frozenset(kwargs.items()))
                keyHash = hashlib.sha1(repr(key).encode()).hexdigest()
                result = cache.get(keyHash)
                if result is None:
                    result = func(self, *args, **kwargs)
                    cache.set(keyHash, result, timeout)
                return result
            else:
                return func(self, *args, **kwargs)
        return wrapper
    return decorator

class CacheManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.model_relation = {}

    def clear(self, model, account, suffix='list'):
        if suffix == '':
            keys_pattern = f"followme.cache.{account}.{model}.*"
        else:
            keys_pattern = f"followme.cache.{account}.{model}.{suffix}.*"
        keys = cache.keys(keys_pattern)

        cache.delete_many(keys=keys)

    def get(self, model, request, pk=''):
        key = self.get_cache_key(model, request, pk)
        return cache.get(key)

    def set(self, model, data, timeout, request, pk=''):
        key = self.get_cache_key(model, request, pk)
        return cache.set(key, data, timeout)

    def get_account(sel, request):
        try:
            auth_header = request.headers.get('Authorization')
            token_key = auth_header.split()[1]
            token = Token.objects.get(key=token_key)

            if token.user.profile.context_account:
                return token.user.profile.context_account.id
            else:
                raise Exception("Fail to detect user context account")

        except Exception as e:
            raise Exception(f"Fail to detect user context account. Error: {str(e)}")

    def get_cache_key(self, model, request, pk=''):
        hashPath = hashlib.sha1(repr(request.path).encode()).hexdigest()
        hashQuery = hashlib.sha1(repr(request.query_params).encode()).hexdigest()
        account = self.get_account(request)

        if (pk != ''):
            key = f"followme.cache.{account}.{model}.{pk}.{hashPath}.{hashQuery}"
        else:
            key = f"followme.cache.{account}.{model}.list.{hashPath}.{hashQuery}"
        return key

    def bind_model(self, model_root, model_class):
        try:
            post_save.connect(self.watch_clear_cache, sender=model_class)
            post_delete.connect(self.watch_clear_cache_delete, sender=model_class)

            for field in model_class._meta.get_fields():
                if isinstance(field, models.ForeignKey):
                    self.bind_related_model(model_root, model_class, field.related_model)
        except Exception as e:
            logging.error(f"Fail to bind watch model in cache. Error: {e}")

    def bind_related_model(self, model, model_class, related_model=None):
        try:
            related_name = related_model.__name__

            if model not in self.model_relation:
                self.model_relation[model] = {
                    "dependend": [],
                    "dependency": [],
                }

            if related_name not in self.model_relation:
                self.model_relation[related_name] = {
                    "dependend": [],
                    "dependency": [],
                }

            if related_name not in self.model_relation[model]["dependend"]:
                self.model_relation[model]["dependend"].append(related_name)

            if model not in self.model_relation[related_name]["dependency"]:
                self.model_relation[related_name]["dependency"].append(model)

            post_save.connect(self.watch_clear_cache, sender=related_model)
            post_save.connect(self.watch_clear_cache, sender=model_class)

            post_delete.connect(self.watch_clear_cache_delete, sender=related_model)
            post_delete.connect(self.watch_clear_cache_delete, sender=model_class)

        except Exception as e:
            logging.error(f"Fail to bind related model in cache. Error: {e}")

    def watch_clear_cache(self, sender, instance, created, **kwargs):
        account = '*'
        if "account" in [f.name for f in instance._meta.get_fields()]:
            account = instance.account.id

        self.clear_cache_tree_by_account(sender.__name__, account)

    def watch_clear_cache_delete(self, sender, instance, **kwargs):
        account = '*'
        if "account" in [f.name for f in instance._meta.get_fields()]:
            account = instance.account.id

        self.clear_cache_tree_by_account(sender.__name__, account)

    def clear_cache_tree_by_account(self, model, account):
        if model in self.model_relation:
            for model_dep in self.model_relation[model]['dependend']:
                self.clear(model_dep, account, '')

            for model_dep in self.model_relation[model]['dependency']:
                self.clear(model_dep, account, '')

        self.clear(model, account, '')

    def clear_cache_tree(self, model, request):
        account = self.get_account(request)
        self.clear_cache_tree_by_account(model, request)

class ModelViewSetCached(ModelViewSet):
    def __init__(self, *args, **kwargs):
        env = environ.Env()

        if env.str("BACKEND_CACHE_TIMEOUT") is None:
            self.cache_timeout = 60
        else:
            self.cache_timeout = env.int("BACKEND_CACHE_TIMEOUT")

        if env.bool("BACKEND_CACHE_ENABLE") == True:
            self.cache_enable = True
        else:
            self.cache_enable = False

        self.cache_manager = CacheManager()

        if hasattr(self, 'serializer_class'):
            self.cache_model = self.serializer_class.Meta.model.__name__
            self.cache_manager.bind_model(self.cache_model, self.serializer_class.Meta.model)
        else:
            if hasattr(self, 'cache_model_class'):
                self.cache_model = self.cache_model_class.__name__
                self.cache_manager.bind_model(self.cache_model, self.cache_model_class)

            else: 
                raise ValueError('Fail: Cache model undefined')

        if hasattr(self, 'cache_related_model_classes'):
            if isinstance(self.cache_related_model_classes, list):
                for related_model in self.cache_related_model_classes:
                    self.cache_manager.bind_model(self.cache_model, related_model)

        super().__init__(*args, **kwargs)

    def list(self, request):
        if self.cache_enable:
            try:
                data = self.cache_manager.get(self.cache_model, request)
                if data is not None:
                    return Response(data)
            except Exception as e:
                logging.error(f"""
                    [CACHE ERROR]: (list): {self.cache_model} model using cache.
                    [ERROR]: {e}"""
                )

            response = super().list(request)

            try:
                self.cache_manager.set(self.cache_model,
                                       response.data,
                                       self.cache_timeout,
                                       request)
            except Exception as e:
                logging.error(f"""
                    [CACHE ERROR]: (list): {self.cache_model} model using cache.
                    [ERROR]: {e}"""
                )

            return response

        else:
            return super().list(request)

    def retrieve(self, request, pk=None):
        if self.cache_enable:
            try:
                data = self.cache_manager.get(self.cache_model, request, pk)
                if data is not None:
                    return Response(data)
            
            except Exception as e:
                logging.error(f"""
                    [CACHE ERROR]: (retrieve): {self.cache_model} model using cache.
                    [ERROR]: {e}"""
                )

            response = super().retrieve(request, pk)

            try:
                self.cache_manager.set(self.cache_model, response.data, self.cache_timeout, request, pk)
            except Exception as e:
                logging.error(f"""
                    [CACHE ERROR]: (retrieve): {self.cache_model} model using cache.
                    [ERROR]: {e}"""
                )

            return response

        else:
            return super().retrieve(request, pk)

    def create(self, request):
        try:
            response = super().create(request)

            try:
                self.cache_manager.clear_cache_tree(self.cache_model, request)
            except Exception as e:
                logging.error(f"""
                    [CACHE ERROR]: (create): {self.cache_model} model using cache.
                    [ERROR]: {e}"""
                )
        except Exception as e:
            response = Response(data=str(e), status=400)

        return response

    def destroy(self, request, pk):
        try:
            super().destroy(request, pk)
        except Exception as e:
            return Response(data=str(e), status=400)

        try:
            self.cache_manager.clear_cache_tree(self.cache_model, request)            
        except Exception as e:
            logging.error(f"""
                [CACHE ERROR]: (destroy): {self.cache_model} model using cache.
                [ERROR]: {e}"""
            )

        return Response(status=204)

    def update(self, request, pk):
        try:
            response = super().update(request, pk)

            try:
                self.cache_manager.clear_cache_tree(self.cache_model, request)
            except Exception as e:
                logging.error(f"""
                    [CACHE ERROR]: (update): {self.cache_model} model using cache.
                    [ERROR]: {e}"""
                )
        except Exception as e:
            response = Response(data=str(e), status=400)

        return response

    def partial_update(self, request, pk):
        try:
            response = super().update(request, pk, partial=True)

            try:
                self.cache_manager.clear_cache_tree(self.cache_model, request)
            except Exception as e:
                logging.error(f"""
                    [CACHE ERROR]: (partial_update): {self.cache_model} model using cache.
                    [ERROR]: {e}"""
                )
        except Exception as e:
            response = Response(data=str(e), status=400)

        return response
