// 最小 Service Worker：只为满足「添加到主屏幕」的安装条件。
// 故意不做任何缓存 —— 避免改完页面后用户还看到旧内容。
// 需要离线能力的话，再往 install 里加 cache.addAll()，并把 fetch 换成缓存优先。

self.addEventListener('install', function () {
  self.skipWaiting();
});

self.addEventListener('activate', function (event) {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', function (event) {
  // 只处理本站 GET 请求，其余交给浏览器默认行为
  if (event.request.method !== 'GET') return;
  if (new URL(event.request.url).origin !== self.location.origin) return;
  event.respondWith(fetch(event.request));
});
