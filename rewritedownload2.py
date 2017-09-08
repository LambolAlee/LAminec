import tqdm
import requests
from time import time
from os import makedirs
from check import check_sha1
from collections import namedtuple
from functools import wraps
import concurrent.futures as Futures
from multiprocessing import cpu_count
from os.path import join, exists, dirname


def timethis(func):
    @wraps(func)
    def decorate(*args):
        start = time()
        failures = func(*args)
        end = time()
        print("Downloading lasts %.2f seconds." % (end-start))
        return failures
    return decorate



def DownloadOne(task, callback=None):
    dirs = dirname(task.path)
    try:
        if not exists(dirs):
            makedirs(dirs)
    except FileExistsError:
        pass
    if callback is None:
        callback = lambda task:None
    r = requests.get(task.url, stream=True, timeout=(10, 50))
    if r.status_code != 200:
        r.raise_for_status()
    with open(task.path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
                f.flush()
        callback(task)
        return task


@timethis
def Download(liblist, title, callback=check_sha1, concurrency=(cpu_count()*4)):
    print("[Lambol]Preparing your futures...")
    with Futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        print("[Lambol]Discovered", len(liblist), "items.")
        print("[Lambol]Start downloading", title, '.')
        futures = gen_futures(liblist, executor, callback)
        done_iter = Futures.as_completed(futures)
        done_iter = tqdm.tqdm(done_iter, total=len(liblist))
        
        canceled, failures, success = process_futures(done_iter, futures)
        if canceled:
            executor.shutdown()
        else:
            print("[Lambol]Downloading {} successfully!".format(title))
        print("[Lambol]Summary:\n\tSuccessfully downloading: %s\n\tFailed: %s" % (success, len(failures)))

    return failures


def gen_futures(liblist, executor, callback):
    futures = {}
    for task in liblist:
        future = executor.submit(DownloadOne, task, callback)
        futures[future] = task
    return futures


def process_futures(done_iter, futures):
    success = 0
    finished = []
    failures = []
    try:
        for future in done_iter:
            err = future.exception()
            if err is None:
                success += 1
                finished.append(future)
            else:
                fail = futures[future]
                failures.append(fail)
        return (False, failures, success)        #return (canceled(bool), failures(list))
    except KeyboardInterrupt:
        done_iter.close()
        print("[Kaniol]Canceling...")
        left_futures = {future:task 
                        for future, task in futures.items()
                        if future not in finished}
        left_futures = tqdm.tqdm(left_futures, total=len(left_futures))
        for future in left_futures:
            failures.append(futures[future])
            future.cancel()
        print("[Kaniol]Shuting down the future executor.")
        return (True, failures, success)