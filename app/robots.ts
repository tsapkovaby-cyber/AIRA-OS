import type {MetadataRoute} from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [{
      userAgent: '*',
      allow: ['/academy', '/learn'],
      disallow: ['/developer', '/dashboard', '/login', '/api'],
    }],
  };
}
