from rest_framework import mixins, viewsets
from rest_framework.response import Response


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """Вьюсет создаёт экземпляр объекта,

    удаляет экземпляр объекта и возвращает список объектов
    """
    pass


class PatchModelMixin(object):
    """
    Частичное обновление экземпляра модели
    """
    def partial_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class NoPutViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.RetrieveModelMixin,
                   PatchModelMixin,
                   viewsets.GenericViewSet):
    """Вьюсет создаёт экземпляр объекта,

    удаляет экземпляр объекта, возвращает список объектов или объект,
    частично обновляет объект. Не обрабатывает PUT-запрос!
    """
    pass
