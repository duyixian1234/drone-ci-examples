import time

import cache


def test_ping():
    assert cache.ping()


def test_set_get():
    cache.set('test', 'test')
    assert cache.get('test').decode() == 'test'

def test_delete():
    cache.set('test', 'test')
    assert cache.delete('test') == 1
    assert not cache.get('test')


def test_setex():
    cache.setex('test', 'test', 2)
    assert cache.get('test').decode() == 'test'
    time.sleep(3)
    assert not cache.get('test')

def test_setnx():
    cache.set('test', 'test')
    assert not cache.setnx('test', 'test2')
    assert cache.get('test').decode() == 'test'
    cache.delete('test')
    assert cache.setnx('test', 'test2')
    assert cache.get('test').decode() == 'test2'
