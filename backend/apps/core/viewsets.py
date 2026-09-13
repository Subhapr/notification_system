"""
Base ViewSet classes ensuring every action (list, retrieve, create,
update, partial_update, destroy) - not just custom @action endpoints -
returns the same {success, message, data} envelope the rest of the
API uses. List responses are wrapped by EnvelopePageNumberPagination;
this handles the non-paginated single-object actions.
"""
from rest_framework import viewsets

from apps.core.responses import success_response


class EnvelopeModelViewSetMixin:
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(data=serializer.data, message="Created successfully.", status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(data=serializer.data, message="Updated successfully.")

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message="Deleted successfully.", status=200)


class EnvelopeModelViewSet(EnvelopeModelViewSetMixin, viewsets.ModelViewSet):
    pass


class EnvelopeReadOnlyModelViewSet(EnvelopeModelViewSetMixin, viewsets.ReadOnlyModelViewSet):
    pass
