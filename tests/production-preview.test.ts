import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";

const read = (path: string) => readFileSync(path, "utf8");

describe("Academy production preview contract", () => {
  it("has a production start command and health endpoint", () => {
    const pkg = JSON.parse(read("package.json"));
    expect(pkg.scripts.start).toBe("next start");
    expect(read("app/api/health/route.ts")).toContain("status: 'ok'");
  });

  it("uses a private owner login and httpOnly session for the restricted developer preview", () => {
    const middleware = read("middleware.ts");
    const loginRoute = read("app/api/developer/login/route.ts");
    const loginPage = read("app/developer-login/page.tsx");
    expect(middleware).toContain("AIRA_PREVIEW_OWNER_EMAIL");
    expect(middleware).toContain("AIRA_PREVIEW_OWNER_PASSWORD");
    expect(middleware).toContain("aira_owner_session");
    expect(middleware).toContain("/developer-login");
    expect(middleware).toContain("/developer/:path*");
    expect(loginRoute).toContain("timingSafeEqual");
    expect(loginRoute).toContain("httpOnly: true");
    expect(loginRoute).toContain('sameSite: "strict"');
    expect(loginPage).toContain("Sign in as Owner");
  });

  it("supports explicit owner logout", () => {
    const logout = read("app/api/developer/logout/route.ts");
    const developerPage = read("app/developer/page.tsx");
    expect(logout).toContain("aira_owner_session");
    expect(logout).toContain("new Date(0)");
    expect(developerPage).toContain("/api/developer/logout");
  });

  it("keeps restricted surfaces out of crawler routes", () => {
    const robots = read("app/robots.ts");
    expect(robots).toContain("'/developer'");
    expect(robots).toContain("'/dashboard'");
    expect(robots).toContain("'/api'");
  });
});
