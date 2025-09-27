addEventListener('fetch', event => {
  event.respondWith(handle(event.request))
})

async function handle(request) {
  const url = new URL(request.url)
  if (!url.pathname.startsWith('/portal/')) return fetch(request)
  const originResp = await fetch(request)
  const headers = new Headers(originResp.headers)
  headers.set('Cache-Control', 'no-store')
  const body = await originResp.arrayBuffer()
  return new Response(body, {
    status: originResp.status,
    statusText: originResp.statusText,
    headers: headers
  })
}
