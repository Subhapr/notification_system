from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class EnvelopePageNumberPagination(PageNumberPagination):
    """
    Wraps DRF's default paginated shape inside the project's standard
    {success, message, data} envelope, so every endpoint - paginated
    or not - is predictable for frontend code.
    """

    page_size = 20

    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "message": "",
                "data": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "results": data,
                },
            }
        )
