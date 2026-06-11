import { Alert, Button, Card, Col, Row, Spin, Statistic, Tag } from "antd";
import type { AdminOverview } from "../services/adminApi";
import { formatNumber, formatTime } from "./format";

interface AdminOverviewProps {
  data: AdminOverview | null;
  loading: boolean;
  error: string;
  onGoKeys: () => void;
}

export function AdminOverviewPanel({ data, loading, error, onGoKeys }: AdminOverviewProps) {
  if (loading && !data) {
    return <Spin size="large" style={{ display: "block", margin: "80px auto" }} />;
  }

  if (error) {
    return <Alert type="error" message={error} showIcon />;
  }

  if (!data) {
    return <Alert type="info" message="暂无总览数据" showIcon />;
  }

  const { licenseSummary, usageStats, persistence } = data;

  return (
    <div>
      {!persistence.likelyPersistent && persistence.warning ? (
        <Alert
          type="warning"
          message="数据持久化风险"
          description={persistence.warning}
          showIcon
          style={{ marginBottom: 16 }}
        />
      ) : null}

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="总秘钥数" value={licenseSummary.totalKeys} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="未使用" value={licenseSummary.unusedKeys} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="已兑换" value={licenseSummary.redeemedKeys} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已发放次数"
              value={licenseSummary.totalCreditsIssued}
              formatter={(v) => formatNumber(Number(v))}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已兑换次数"
              value={licenseSummary.totalCreditsRedeemed}
              formatter={(v) => formatNumber(Number(v))}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="当前在线" value={usageStats.online} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="累计访客" value={usageStats.totalVisitors} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="访问次数" value={usageStats.visits} />
          </Card>
        </Col>
      </Row>

      <Card
        title="最近动态"
        style={{ marginTop: 16 }}
        extra={
          <Button type="primary" onClick={onGoKeys}>
            前往秘钥管理
          </Button>
        }
      >
        <p>
          最近创建: {formatTime(licenseSummary.latestCreatedAt)}
        </p>
        <p>
          最近兑换: {formatTime(licenseSummary.latestRedeemedAt)}
        </p>
        <p>
          持久化状态:{" "}
          <Tag color={persistence.likelyPersistent ? "success" : "warning"}>
            {persistence.likelyPersistent ? "正常" : "需关注"}
          </Tag>
        </p>
      </Card>
    </div>
  );
}
