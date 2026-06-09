import { cn } from "../../lib/cn";

interface SkeletonProps {
  className?: string;
  lines?: number;
}

export function Skeleton({ className, lines = 3 }: SkeletonProps) {
  return (
    <div className={cn("interpret-skeleton", className)} aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="interpret-skeleton-line"
          style={{ width: `${88 - i * 12}%` }}
        />
      ))}
    </div>
  );
}

export function InterpretSkeleton() {
  return (
    <div className="interpret-skeleton-wrap" role="status" aria-label="解读生成中">
      <Skeleton lines={5} />
      <p className="interpret-stage-hint">正在组织盘面与生成解读...</p>
    </div>
  );
}
