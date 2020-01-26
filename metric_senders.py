from math import inf

import requests

from credentials import Credentials
from errors import NoLabelsError, NotSortedError


class BasePushpromMetricSender:
    """
    This is common class of metric sender. It can be used to send any type of metrics, but if you want to follow
    prometheus concepts of metric types https://prometheus.io/docs/concepts/metric_types/ - you can use inheritor
    classes below or write your own classes.
    """

    def __init__(self, credentials: Credentials, metric_name: str, help_string: str, metric_type: str):
        self.url = credentials.address

        if len(metric_name) > 0:
            self.metric_name = metric_name
        else:
            raise ValueError("Field metric_name should not be empty!")

        if metric_type == "counter" or \
                metric_type == "gauge" or \
                metric_type == "histogram" or \
                metric_type == "summary":
            self.metric_type = metric_type
        else:
            self.metric_type = "gauge"

        if isinstance(help_string, str):
            self.help = help_string
        else:
            raise TypeError("Field help should be str.")

    def send(self, value: float, labels: dict) -> requests.Response:
        """
        This method is for sending some values of a metric with labels.
        :param value: actual value we want to send
        :param labels: labels, such as method name, datasource name or other additional info
        :return: http response from pushprom
        """
        if isinstance(labels, dict):
            raise NoLabelsError("Can not send metrics: labels should be a type of dict.")
        if len(labels) < 1:
            raise NoLabelsError("Can not send metrics: no labels provided.")
        json = {
            "type": self.metric_type,
            "name": self.metric_name,
            "help": self.help,
            "method": "add",
            "value": value,
            "labels": labels
        }
        response = requests.post(self.url, json=json)
        return response


class Gauge(BasePushpromMetricSender):

    def __init__(self, credentials: Credentials, metric_name: str, help_string: str):
        super(Gauge, self).__init__(credentials=credentials,
                                    metric_name=metric_name,
                                    help_string=help_string,
                                    metric_type="gauge")
        self.__counter = 0.0

    @property
    def counter(self) -> float:
        return self.__counter

    def increase_by(self, value: float):
        self.__counter += value

    def decrease_by(self, value: float):
        self.__counter -= value

    def send_gauge(self, labels: dict) -> requests.Response:
        """
        This class sends current gauge value.
        :param labels: labels, such as method name, datasource name or other additional info
        :return: http response from pushprom
        """
        return super(Gauge, self).send(value=self.__counter, labels=labels)


class Counter(BasePushpromMetricSender):

    def __init__(self, credentials: Credentials, metric_name: str, help_string: str):
        super(Counter, self).__init__(credentials=credentials,
                                      metric_name=metric_name,
                                      help_string=help_string,
                                      metric_type="counter")
        self.__counter = 0

    @property
    def counter(self) -> int:
        return self.__counter

    def increase(self):
        self.__counter += 1

    def reset(self):
        self.__counter = 0

    def send_counter(self, labels: dict) -> requests.Response:
        """
        This class sends current counter value.
        :param labels: labels, such as method name, datasource name or other additional info
        :return: http response from pushprom
        """
        return super(Counter, self).send(value=self.__counter, labels=labels)


class Histogram(BasePushpromMetricSender):
    default_buckets = (.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0, inf)

    def __init__(self, credentials: Credentials, metric_name: str, help_string: str, buckets_bounds=default_buckets):
        raise NotImplementedError("Kindly sorry: this class is not implemented yet.")
        super(Histogram, self).__init__(credentials=credentials,
                                        metric_name=metric_name,
                                        help_string=help_string,
                                        metric_type="histogram")
        self.__sum = 0.0
        self.__count = 0
        self.__buckets = {}
        if buckets_bounds != sorted(buckets_bounds):
            raise NotSortedError("Buckets bounds are not sorted.")
        if buckets_bounds[-1] != inf:
            buckets_bounds = tuple(list(buckets_bounds).append(inf))
        for item in buckets_bounds:
            self.__buckets[item] = 0

    def add_value(self, value: float):
        self.__sum += value
        self.__count += 1
        for bound, counter in self.__buckets.items():  # type: float, int
            if value <= bound:
                counter += 1
                break

    @property
    def total_sum(self) -> float:
        return self.__sum

    @property
    def count(self) -> int:
        return self.__count

    @property
    def buckets(self) -> dict:
        return self.__buckets


class Summary(BasePushpromMetricSender):

    def __init__(self, credentials: Credentials, metric_name: str, help_string: str):
        raise NotImplementedError("Kindly sorry: this class is not implemented yet.")
        super(Histogram, self).__init__(credentials=credentials,
                                        metric_name=metric_name,
                                        help_string=help_string,
                                        metric_type="summary")
