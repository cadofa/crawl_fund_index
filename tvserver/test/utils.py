url_pattern = list()

def url_prefix(url):
    def wrap_class(class_):
        url_pattern.append((url, class_))
        return url_pattern
    return wrap_class
