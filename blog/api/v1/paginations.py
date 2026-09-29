from rest_framework import pagination
from rest_framework.response import Response


class DefaultPagination(pagination.PageNumberPagination):
    page_size = 2

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "total_post": self.page.paginator.count,
                "total_page": self.page.paginator.num_pages,
                "results": data,
            }
        )


class DefaultPaginationComments(pagination.PageNumberPagination):
    page_size = 3

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "total_comments": self.page.paginator.count,
                "total_page": self.page.paginator.num_pages,
                "results": data,
            }
        )


class DefaultPaginationCategory(pagination.PageNumberPagination):
    page_size = 2

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "total_category": self.page.paginator.count,
                "total_page": self.page.paginator.num_pages,
                "results": data,
            }
        )
