import { Alert, Card, Descriptions, Spin } from "antd";
import type { AdminOverview } from "../services/adminApi";

interface SystemHealthProps {
  data: AdminOverview | null;
  loading: boolean;
  error: string;
}

export function SystemHealthPanel({ data, loading, error }: SystemHealthProps) {
  if (loading && !data) {
    return <Spin size="large" style={{ display: "block", margin: "80px auto" }} />;
  }

  if (error) {
    return <Alert type="error" message={error} showIcon />;
  }

  if (!data) {
    return <Alert type="info" message="暂无健康检查数据" showIcon />;
  }

  const { usageStats, persistence } = data;

  return (
    <div>
      {!persistence.likelyPersistent && persistence.warning ? (
        <Alert
          type="error"
          message="持久化风险"
          description={persistence.warning}
          showIcon
          style={{ marginBottom: 16 }}
        />
      ) : (
        <Alert
          type="success"
          message="数据持久化检查通过"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Card title="访问统计" style={{ marginBottom: 16 }}>
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="当前在线">{usageStats.online}</Descriptions.Item>
          <Descriptions.Item label="累计访客">{usageStats.totalVisitors}</Descriptions.Item>
          <Descriptions.Item label="访问次数">{usageStats.visits}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="数据库路径">
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="配额数据库">
            <span className="admin-mono">{persistence.quotaDbPath}</span>
          </Descriptions.Item>
          <Descriptions.Item label="统计数据库">
            <span className="admin-mono">{persistence.statsDbPath}</span>
          </Descriptions.Item>
          <Descriptions.Item label="持久化状态">
            {persistence.likelyPersistent ? "已挂载持久存储" : "可能非持久存储"}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
}
