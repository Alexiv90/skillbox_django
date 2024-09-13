from datetime import datetime,timedelta

from django.http import HttpRequest,HttpResponse


def set_useragent_on_request_middleware(get_response):

    print("initial call")

    def middleware(request: HttpRequest) -> HttpResponse:
        print("beefore get response")
        request.user_agent = request.META['HTTP_USER_AGENT']
        response = get_response(request)
        print("after get response")
        return response

    return middleware


class CountRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.request_time = {}
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest) -> HttpResponse:

        time_check = timedelta(seconds=20)
        time_delly = timedelta(seconds=5)

        if self.request_time:
            print("last request time", self.request_time["time"])
            print("current request time", datetime.now())
            if self.request_time["ipaddress"] == request.META.get('REMOTE_ADDR') and (datetime.now() - self.request_time["time"]) > time_check:
                time_diff = datetime.now() - self.request_time["time"]
                ban_time = time_delly - time_diff
                if ban_time.total_seconds() > 0:
                    return HttpResponse(f"Too many requests, you can retry after {ban_time.total_seconds()} seconds")
                else:
                    print("new request time", self.request_time["time"])
                    self.request_time = {"time": datetime.now(), "ipaddress": request.META.get('REMOTE_ADDR')}
        else:
            self.request_time = {"time": datetime.now(), "ipaddress": request.META.get('REMOTE_ADDR')}
            print("first request time", self.request_time["time"])

        self.requests_count += 1
        print("requests count", self.requests_count)
        response = self.get_response(request)
        print("responses count", self.responses_count)
        self.responses_count += 1
        return response

    def process_exceptions(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print("got", self.exceptions_count, "exceptions")