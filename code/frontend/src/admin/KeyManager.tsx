import {
  Alert,
  Button,
  DatePicker,
  Drawer,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Table,
  Tag,
  message,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import type { Dayjs } from "dayjs";
import { useCallback, useEffect, useState } from "react";
import {
  adminGenerateKeys,
  adminListKeys,
  type GeneratedKey,
  type LicenseKeyRecord,
} from "../services/adminApi";
import { KEY_TIERS } from "./adminTypes";
import { formatTime } from "./format";

const PAGE_SIZE = 20;

interface FilterFormValues {
  status?: "" | "unused" | "redeemed";
  tier?: number;
  note?: string;
  redeemedDeviceId?: string;
  createdRange?: [Dayjs, Dayjs];
}

interface GenerateFormValues {
  tier: number;
  count: number;
  note?: string;
}

interface KeyManagerProps {
  refreshToken: number;
  onDataChanged: () => void;
}

export function KeyManager({ refreshToken, onDataChanged }: KeyManagerProps) {
  const [filterForm] = Form.useForm<FilterFormValues>();
  const [generateForm] = Form.useForm<GenerateFormValues>();

  const [records, setRecords] = useState<LicenseKeyRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState<GeneratedKey[]>([]);

  const buildQuery = useCallback(
    (currentPage: number, filters: FilterFormValues) => {
      const range = filters.createdRange;
      return {
        limit: PAGE_SIZE,
        offset: (currentPage - 1) * PAGE_SIZE,
        status: filters.status || undefined,
        tier: filters.tier,
        note: filters.note?.trim() || undefined,
        redeemedDeviceId: filters.redeemedDeviceId?.trim() || undefined,
        createdFrom: range?.[0] ? range[0].startOf("day").unix() : undefined,
        createdTo: range?.[1] ? range[1].endOf("day").unix() : undefined,
      };
    },
    [],
  );

  const loadList = useCallback(
    async (currentPage: number, filters: FilterFormValues) => {
      setLoading(true);
      setError("");
      try {
        const data = await adminListKeys(buildQuery(currentPage, filters));
        setRecords(data.items);
        setTotal(data.total);
      } catch (err) {
        setError(err instanceof Error ? err.message : "加载失败");
      } finally {
        setLoading(false);
      }
    },
    [buildQuery],
  );

  useEffect(() => {
    const filters = filterForm.getFieldsValue();
    void loadList(page, filters);
  }, [page, refreshToken, loadList, filterForm]);

  const handleSearch = async () => {
    const values = await filterForm.validateFields();
    setPage(1);
    await loadList(1, values);
  };

  const handleReset = async () => {
    filterForm.resetFields();
    setPage(1);
    await loadList(1, {});
  };

  const copyText = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      message.success("已复制到剪贴板");
    } catch {
      message.error("复制失败, 请手动复制");
    }
  };

  const handleGenerate = async (values: GenerateFormValues) => {
    setGenerating(true);
    try {
      const keys = await adminGenerateKeys({
        tier: values.tier,
        count: values.count,
        note: (values.note || "").trim(),
      });
      setGenerated(keys);
      message.success(`已生成 ${keys.length} 个秘钥`);
      onDataChanged();
      const filters = filterForm.getFieldsValue();
      await loadList(page, filters);
    } catch (err) {
      message.error(err instanceof Error ? err.message : "生成失败");
    } finally {
      setGenerating(false);
    }
  };

  const columns: ColumnsType<LicenseKeyRecord> = [
    { title: "ID", dataIndex: "id", width: 70 },
    {
      title: "面额",
      dataIndex: "tierLabel",
      width: 80,
      render: (value: string) => `${value} 元`,
    },
    { title: "次数", dataIndex: "credits", width: 80 },
    {
      title: "状态",
      dataIndex: "status",
      width: 90,
      render: (value: string) =>
        value === "unused" ? <Tag color="gold">未使用</Tag> : <Tag color="green">已兑换</Tag>,
    },
    {
      title: "备注",
      dataIndex: "note",
      ellipsis: true,
      render: (value: string | null) => value || "-",
    },
    {
      title: "创建时间",
      dataIndex: "createdAt",
      width: 170,
      render: (value: number) => formatTime(value),
    },
    {
      title: "兑换设备",
      dataIndex: "redeemedDeviceId",
      ellipsis: true,
      render: (value: string | null) =>
        value ? <span className="admin-mono">{value}</span> : "-",
    },
    {
      title: "兑换时间",
      dataIndex: "redeemedAt",
      width: 170,
      render: (value: number | null) => formatTime(value),
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={() => setDrawerOpen(true)}>
          生成秘钥
        </Button>
        <Button onClick={() => void handleSearch()}>刷新列表</Button>
      </Space>

      <Form
        form={filterForm}
        layout="inline"
        className="admin-filter-form"
        onFinish={() => void handleSearch()}
      >
        <Form.Item name="status" label="状态">
          <Select
            allowClear
            placeholder="全部"
            style={{ width: 120 }}
            options={[
              { value: "unused", label: "未使用" },
              { value: "redeemed", label: "已兑换" },
            ]}
          />
        </Form.Item>
        <Form.Item name="tier" label="面额">
          <Select
            allowClear
            placeholder="全部"
            style={{ width: 140 }}
            options={KEY_TIERS.map((item) => ({
              value: item.value,
              label: item.label,
            }))}
          />
        </Form.Item>
        <Form.Item name="note" label="备注">
          <Input placeholder="关键词" allowClear style={{ width: 160 }} />
        </Form.Item>
        <Form.Item name="redeemedDeviceId" label="兑换设备">
          <Input placeholder="设备 ID" allowClear style={{ width: 180 }} />
        </Form.Item>
        <Form.Item name="createdRange" label="创建时间">
          <DatePicker.RangePicker />
        </Form.Item>
        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit">
              查询
            </Button>
            <Button onClick={() => void handleReset()}>重置</Button>
          </Space>
        </Form.Item>
      </Form>

      {error ? <Alert type="error" message={error} showIcon style={{ marginBottom: 12 }} /> : null}

      <Table<LicenseKeyRecord>
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={records}
        scroll={{ x: 960 }}
        pagination={{
          current: page,
          pageSize: PAGE_SIZE,
          total,
          showSizeChanger: false,
          showTotal: (value) => `共 ${value} 条`,
          onChange: (nextPage) => setPage(nextPage),
        }}
      />

      <Drawer
        title="生成秘钥"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={480}
        destroyOnClose
      >
        <Form<GenerateFormValues>
          form={generateForm}
          layout="vertical"
          initialValues={{ tier: 10, count: 1, note: "" }}
          onFinish={(values) => void handleGenerate(values)}
        >
          <Form.Item
            label="面额"
            name="tier"
            rules={[{ required: true, message: "请选择面额" }]}
          >
            <Select
              options={KEY_TIERS.map((item) => ({
                value: item.value,
                label: item.label,
              }))}
            />
          </Form.Item>
          <Form.Item
            label="数量"
            name="count"
            rules={[{ required: true, message: "请输入数量" }]}
          >
            <InputNumber min={1} max={100} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="备注" name="note">
            <Input placeholder="买家/订单备注" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={generating} block>
              生成秘钥
            </Button>
          </Form.Item>
        </Form>

        {generated.length > 0 ? (
          <div style={{ marginTop: 20 }}>
            <Space style={{ marginBottom: 12 }}>
              <strong>本次生成的明文秘钥 (仅显示一次)</strong>
              <Button
                size="small"
                onClick={() => void copyText(generated.map((item) => item.key).join("\n"))}
              >
                复制全部
              </Button>
            </Space>
            <ul className="admin-key-result-list">
              {generated.map((item) => (
                <li key={item.key} className="admin-key-result-item">
                  <code className="admin-mono">{item.key}</code>
                  <span>
                    {item.tier} 元 / {item.credits} 次
                  </span>
                  <Button size="small" onClick={() => void copyText(item.key)}>
                    复制
                  </Button>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </Drawer>
    </div>
  );
}
