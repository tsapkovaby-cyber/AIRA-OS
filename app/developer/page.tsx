import Link from "next/link";

const capabilities = [
  "All Academy plans and features",
  "All 10 learning languages",
  "Learning-path inspection",
  "Voice and video feature preview",
  "Future billing/subscription inspection",
  "Pre-release feature access",
];

export default function DeveloperPreview() {
  return (
    <main>
      <div className="page-head">
        <div>
          <p className="eyebrow">AIRA Academy · Restricted</p>
          <h1>Owner / Developer access</h1>
          <p className="muted">Administrative access is a role, not a purchasable student plan.</p>
        </div>
        <div>
          <span className="health">● OWNER MODE</span>
          <form action="/api/developer/logout" method="post" style={{ marginTop: 12 }}>
            <button className="button" type="submit">Sign out</button>
          </form>
        </div>
      </div>
      <section className="brief">
        <div>
          <span className="eyebrow">Security boundary</span>
          <h2>Founder access stays separate from subscriptions.</h2>
          <span>Production authorization is resolved server-side from the owner credentials configured in the deployment environment. Client-provided owner flags are never trusted.</span>
        </div>
      </section>
      <div className="grid">
        {capabilities.map((item) => (
          <article className="card" key={item}>
            <strong>{item}</strong>
            <p className="muted">Included for authorized Owner / Developer accounts.</p>
          </article>
        ))}
      </div>
      <section className="card">
        <h2>Academy preview</h2>
        <p className="muted">Open the live Academy while keeping owner tools behind the private developer session.</p>
        <Link href="/academy">Open AIRA Academy →</Link>
      </section>
    </main>
  );
}
