import { createHash } from 'crypto';
import { readFileSync } from 'fs';
import { resolve } from 'path';

export default function nonceInjector() {
  let config;
  
  return {
    name: 'vite-plugin-nonce-injector',
    configResolved(resolvedConfig) {
      config = resolvedConfig;
    },
    
    transformIndexHtml: {
      enforce: 'pre',
      transform(html) {
        // Only inject nonce in development
        if (config.command === 'serve') {
          const nonce = createHash('sha256')
            .update(Math.random().toString())
            .digest('base64');
            
          // Replace nonce placeholders
          return html
            .replace(/<%= nonce %>/g, nonce)
            .replace(/__CSP_NONCE_PLACEHOLDER__/g, nonce);
        }
        return html;
      },
    },
    
    configureServer(server) {
      return () => {
        server.middlewares.use((req, res, next) => {
          const nonce = createHash('sha256')
            .update(Math.random().toString())
            .digest('base64');
            
          // Add nonce to response headers for client-side use
          res.setHeader('X-CSP-Nonce', nonce);
          next();
        });
      };
    },
  };
}
