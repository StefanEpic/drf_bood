from rest_framework.filters import SearchFilter


class TitleSearchFilter(SearchFilter):
    search_description = "Search by title."


class DateSearchFilter(SearchFilter):
    search_description = "Search by date."
