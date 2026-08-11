export type SystemHealth='SYSTEM_HEALTHY'|'SYSTEM_DEGRADED'|'SYSTEM_PAUSED'|'SYSTEM_CRITICAL';
export function statusLabel(status:SystemHealth){return ({SYSTEM_HEALTHY:'Healthy',SYSTEM_DEGRADED:'Degraded',SYSTEM_PAUSED:'Paused',SYSTEM_CRITICAL:'Critical'})[status]}
export function canPerform(role:string,action:string){if(role==='OWNER')return true;if(action==='VIEW')return ['ADMIN','REVIEWER','EDITOR','ANALYST','VIEWER'].includes(role);return false}
