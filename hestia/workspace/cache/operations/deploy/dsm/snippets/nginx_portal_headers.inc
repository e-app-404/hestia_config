# nginx include: portal headers and asset caching
# Drop this file on the Synology NAS (suggested path: /usr/local/nginx/includes/portal_headers.inc)
# This file contains only location blocks and is intended to be included inside the
# existing server block for nas.xplab.io. Do NOT place it directly under /etc/nginx/conf.d
# as that would create a separate server block and risk conflicts.

##########################
# Portal and asset headers
##########################

## Ensure portal pages are never cached by intermediaries or browser
location ^~ /portal/ {
  # Serve files normally, then allow header overrides
  try_files $uri $uri/ =404;

  # Explicitly prevent caching of portal pages
  add_header Cache-Control "no-store" always;

  # Minimal, conservative CSP for portal pages (tweak as needed)
  add_header Content-Security-Policy "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; frame-ancestors 'self';" always;
}

## Long-lived caching for static assets as a fallback at origin
location ~* \.(js|css|woff2?|svg|ico|png|jpg|jpeg)$ {
  # Only set this if your origin/webserver is not already setting a long max-age
  add_header Cache-Control "public, max-age=31536000, immutable" always;
  try_files $uri $uri/ =404;
}
