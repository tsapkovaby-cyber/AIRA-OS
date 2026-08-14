import {describe,it,expect} from 'vitest';
import fs from 'node:fs';

describe('AIRA Academy PWA',()=>{
  it('ships an installable manifest',()=>{
    const manifest=JSON.parse(fs.readFileSync('public/manifest.webmanifest','utf8'));
    expect(manifest.name).toBe('AIRA Academy');
    expect(manifest.start_url).toBe('/academy');
    expect(manifest.display).toBe('standalone');
    expect(manifest.icons.length).toBeGreaterThanOrEqual(2);
  });

  it('ships a service worker and offline fallback',()=>{
    const worker=fs.readFileSync('public/sw.js','utf8');
    const offline=fs.readFileSync('app/offline/page.tsx','utf8');
    expect(worker).toContain("caches.match('/offline')");
    expect(worker).toContain("'/academy'");
    expect(offline).toContain('You are offline.');
  });
});
