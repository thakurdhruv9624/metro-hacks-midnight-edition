import { useEffect, useState } from "react";
import { api, type Comparison as ComparisonData } from "../lib/api";
import { Card, EmptyState, ErrorState, Heading, Screen, Skeleton } from "../components/ui";

export function Comparison() {
  const [data, setData] = useState<ComparisonData | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error" | "empty">("loading");
  const [error, setError] = useState("");

  const load = () => {
    setStatus("loading");
    api
      .comparison()
      .then((body) => {
        setData(body);
        setStatus(body.metrics.length ? "ready" : "empty");
      })
      .catch((err: Error) => {
        setError(err.message);
        setStatus("error");
      });
  };

  useEffect(load, []);

  return (
    <Screen>
      <Heading kicker="Last mile" title="Before and after" />
      {status === "loading" ? <Skeleton className="h-48" /> : null}
      {status === "error" ? <ErrorState message={error} onRetry={load} /> : null}
      {status === "empty" ? (
        <EmptyState title="No comparison yet" body="Train the demand model, then return here." />
      ) : null}
      {status === "ready" && data ? (
        <>
          <p className="mb-8 max-w-[560px] text-[17px] leading-7 text-mute">{data.narrative}</p>
          <div className="grid gap-4 md:grid-cols-3">
            {data.metrics.map((metric) => (
              <Card key={metric.label}>
                <p className="text-[14px] text-mute">{metric.label}</p>
                <div className="mt-6 flex items-end justify-between">
                  <div>
                    <p className="text-[13px] text-mute">Today</p>
                    <p className="text-[22px] font-medium">
                      {metric.baseline} {metric.unit}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-[13px] text-mute">MetroSync</p>
                    <p className="text-[22px] font-medium text-accent">
                      {metric.metrosync} {metric.unit}
                    </p>
                  </div>
                </div>
                <p className="mt-4 text-[13px] text-mute">{metric.delta_pct}% change</p>
              </Card>
            ))}
          </div>
        </>
      ) : null}
    </Screen>
  );
}
