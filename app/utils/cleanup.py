import os
import time


def cleanup_results(folder = "results", ttl_second = 3600):
    now = time.time()
    for filename in os.listdir(folder):
        path = os.path.join(folder,filename)

        if os.path.isfile(path):
            file_age = now - os.path.getmtime(path)
            if file_age > ttl_second:
                try:
                    os.remove(path)
                except Exception:
                    pass

