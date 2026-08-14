import {describe,it,expect} from 'vitest';
import {readFileSync} from 'node:fs';

const read=(path:string)=>readFileSync(path,'utf8');

describe('Academy production preview contract',()=>{
  it('has a production start command and health endpoint',()=>{
    const pkg=JSON.parse(read('package.json'));
    expect(pkg.scripts.start).toBe('next start');
    expect(read('app/api/health/route.ts')).toContain("status: 'ok'");
  });

  it('fails closed for the restricted developer preview',()=>{
    const middleware=read('middleware.ts');
    expect(middleware).toContain('AIRA_PREVIEW_OWNER_EMAIL');
    expect(middleware).toContain('AIRA_PREVIEW_OWNER_PASSWORD');
    expect(middleware).toContain('/developer/:path*');
    expect(middleware).toContain('status: 401');
  });

  it('keeps restricted surfaces out of crawler routes',()=>{
    const robots=read('app/robots.ts');
    expect(robots).toContain("'/developer'");
    expect(robots).toContain("'/dashboard'");
    expect(robots).toContain("'/api'");
  });
});
