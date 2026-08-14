import Link from 'next/link';

export default function OfflinePage(){return <main className="academy-preview"><section className="academy-hero"><p className="eyebrow">AIRA Academy · Offline</p><h1>You are offline.</h1><p className="muted">Previously cached Academy pages can still be available. Reconnect to sync new lessons, tutor conversations and progress.</p><div className="academy-actions"><Link className="primary-action" href="/academy">Return to Academy</Link></div></section></main>}
