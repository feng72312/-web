import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const mcpPath =
  'C:\\Users\\liqingfeng\\AppData\\Local\\npm-global\\node_modules\\@cloudbase\\cloudbase-mcp\\dist\\index.cjs';
const { getCloudBaseManager } = require(mcpPath);

const ENV_ID = 'zy-feng-d3glt5d93b1a9f08e';
const SERVER = 'bazi-rag';
const OUT_DIR = path.join('d:\\ZY');

async function main() {
  const manager = await getCloudBaseManager({
    cloudBaseOptions: { envId: ENV_ID },
    authStrategy: 'fail_fast',
  });
  if (!manager) throw new Error('CloudBase not logged in');

  const records = await manager.cloudrun.getDeployRecords({ serverName: SERVER });
  const latest = records?.DeployRecords?.[0];
  if (!latest) throw new Error('no deploy records');

  const lines = [];
  lines.push(`# bazi-rag deploy diagnostics`);
  lines.push(`DeployId: ${latest.DeployId}`);
  lines.push(`Status: ${latest.Status}`);
  lines.push(`DeployTime: ${latest.DeployTime}`);
  lines.push(`RunId: ${latest.RunId}`);
  lines.push(`BuildId: ${latest.BuildId}`);
  lines.push('');

  const process = await manager.cloudrun.getProcessLog({ RunId: latest.RunId });
  lines.push('## Process log (platform deploy steps)');
  lines.push(...(process?.Logs || []));
  lines.push('');

  if (latest.BuildId) {
    const build = await manager.cloudrun.getBuildLog({
      serverName: SERVER,
      buildId: latest.BuildId,
    });
    const text = build?.Log?.Text || '';
    lines.push('## Build log tail (last 4000 chars)');
    lines.push(text.slice(-4000));
    lines.push('');
    fs.writeFileSync(
      path.join(OUT_DIR, `bazi-rag-${latest.DeployId}-build.log`),
      text,
      'utf8'
    );
  }

  const svc = manager.cloudrun;
  const apis = [
    ['DescribeCloudBaseRunOperateBasic', { EnvId: ENV_ID, RunId: latest.RunId }],
    ['DescribeServerManageTask', { EnvId: ENV_ID, ServerName: SERVER, TaskId: 0 }],
    ['DescribeReleaseOrder', { EnvId: ENV_ID, ServerName: SERVER }],
  ];

  for (const [action, payload] of apis) {
    try {
      const res = await svc.tcbrService.request(action, payload);
      lines.push(`## ${action}`);
      lines.push(JSON.stringify(res, null, 2));
      lines.push('');
    } catch (err) {
      lines.push(`## ${action} ERROR`);
      lines.push(String(err?.message || err));
      lines.push('');
    }
  }

  // tcb API for older run process log variant
  try {
    const tcbSvc = svc.tcbService;
    const alt = await tcbSvc.request('DescribeCloudBaseRunProcessLog', {
      EnvId: ENV_ID,
      RunId: latest.RunId,
    });
    lines.push('## DescribeCloudBaseRunProcessLog (tcb)');
    lines.push(JSON.stringify(alt, null, 2));
    lines.push('');
  } catch (err) {
    lines.push(`## DescribeCloudBaseRunProcessLog ERROR: ${err?.message || err}`);
    lines.push('');
  }

  try {
    const alt2 = await svc.tcbService.request('DescribeCloudBaseRunOperateBasic', {
      EnvId: ENV_ID,
      RunId: latest.RunId,
    });
    lines.push('## DescribeCloudBaseRunOperateBasic (failure reason)');
    lines.push(JSON.stringify(alt2, null, 2));
    lines.push('');
  } catch (err) {
    lines.push(`## DescribeCloudBaseRunOperateBasic ERROR: ${err?.message || err}`);
    lines.push('');
  }

  const detail = await manager.cloudrun.detail({ serverName: SERVER });
  lines.push('## Online versions');
  lines.push(JSON.stringify(detail?.OnlineVersionInfos, null, 2));
  lines.push('');
  lines.push('## Console links');
  lines.push(`Env: https://tcb.cloud.tencent.com/dev?envId=${ENV_ID}`);
  lines.push(
    `Run service: https://tcb.cloud.tencent.com/dev?envId=${ENV_ID}#/platform-run/service/detail?serverName=${SERVER}`
  );
  lines.push(
    'Deploy history: open service -> Deploy/Publish tab -> version history -> click failed version -> release details'
  );
  lines.push(
    'Runtime stdout: open service -> Logs tab -> filter version bazi-rag-0XX -> category stdout'
  );

  const outPath = path.join(OUT_DIR, `bazi-rag-${latest.DeployId}-diagnostics.txt`);
  fs.writeFileSync(outPath, lines.join('\n'), 'utf8');
  console.log('[saved]', outPath);
  if (latest.BuildId) {
    console.log('[saved]', path.join(OUT_DIR, `bazi-rag-${latest.DeployId}-build.log`));
  }
}

main().catch((err) => {
  console.error('[failed]', err?.message || err);
  process.exit(1);
});
