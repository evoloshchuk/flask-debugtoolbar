from flask import current_app
from flask_debugtoolbar.panels import DebugPanel
from flask_debugtoolbar.utils import format_fname
try:
    from flask.ext.cache import get_debug_requests
except ImportError:
    cache_available = False
    get_debug_requests =  None
else:
    cache_available = True


class CacheDebugPanel(DebugPanel):
    """Panel that displays cache request debug information."""

    name = 'Cache'

    def __init__(self, jinja_env, context={}):
        DebugPanel.__init__(self, jinja_env, context=context)
        if current_app.config.get('DEBUG_TB_CACHE_ENABLED'):
            self.is_active = True

    @property
    def has_content(self):
        if not cache_available:
            return False
        return bool(get_debug_requests())

    def nav_title(self):
        return 'Cache'

    def title(self):
        return 'Cache Requests'

    def nav_subtitle(self):
        if not self.is_active or not cache_available:
            return 'Unavailable'
        # Aggregate stats.
        stats = {'hit': 0, 'miss': 0, 'time': 0}
        for log in get_debug_requests():
            stats[log.hit and 'hit' or 'miss'] += 1
            stats['time'] += log.duration
        stats['time'] = round(stats['time'], 2)
        return '%(hit)s hits, %(miss)s misses in %(time)sms' % stats

    def content(self):
        if not self.is_active or not cache_available:
            return 'Cache profiler not activated'
        requests = []
        counter = 0

        for log in get_debug_requests():
            requests.append({'id': counter,
                             'hit': log.hit,
                             'method': log.method,
                             'parameters': log.parameters,
                             'result': log.result,
                             'duration': log.duration,
                             'context': format_fname(log.context)})
            counter += 1
        return self.render('panels/cache.html', {'requests': requests})

    def url(self):
        return ''
