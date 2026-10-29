from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.templatetags.static import static

CACHE_VERSION = 'library-v1'


def manifest(request):
    data = {
        "name": "مكتبة الجامعة",
        "short_name": "المكتبة",
        "description": "نظام إدارة مكتبة جامعية - استعارة وبحث عن الكتب",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "orientation": "portrait",
        "dir": "rtl",
        "lang": "ar",
        "background_color": "#14232d",
        "theme_color": "#14232d",
        "icons": [
            {"src": static("library/icons/icon-192.png"), "sizes": "192x192",
             "type": "image/png", "purpose": "any maskable"},
            {"src": static("library/icons/icon-512.png"), "sizes": "512x512",
             "type": "image/png", "purpose": "any maskable"},
        ],
    }
    return JsonResponse(data, content_type="application/manifest+json")


def service_worker(request):
    js = """
const CACHE = '%(version)s';
const PRECACHE = ['/offline/', '%(icon)s'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // الملفات الثابتة (محلية أو CDN): من الكاش أولاً
  if (url.pathname.startsWith('/static/') || url.hostname.includes('cdn.jsdelivr.net')) {
    e.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy));
        return res;
      }))
    );
    return;
  }

  // الصفحات: من الشبكة أولاً، وصفحة بلا اتصال عند الفشل
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).catch(() => caches.match('/offline/')));
  }
});
""" % {"version": CACHE_VERSION, "icon": static("library/icons/icon-192.png")}
    response = HttpResponse(js, content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache"
    return response


def offline(request):
    return render(request, "library/offline.html")
