import { motion } from "framer-motion";
import type { ReactNode } from "react";

const ease = [0.25, 0.1, 0.25, 1] as const;

export function Screen({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.24, ease }}
      className="mx-auto w-full max-w-[720px] px-6 pb-16 pt-6 md:max-w-[1080px]"
    >
      {children}
    </motion.div>
  );
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-card bg-white p-6 shadow-card ${className}`}>{children}</div>;
}

export function Button({
  children,
  onClick,
  disabled,
  type = "button",
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  type?: "button" | "submit";
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className="h-12 w-full rounded-[16px] bg-accent text-[16px] font-medium text-white transition-opacity duration-200 ease-out enabled:hover:opacity-90 disabled:opacity-40"
    >
      {children}
    </button>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-2xl bg-[#EFEFF4] ${className}`} />;
}

export function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <Card>
      <p className="text-[20px] font-medium text-ink">Something paused</p>
      <p className="mt-2 text-[15px] text-mute">{message}</p>
      <div className="mt-6">
        <Button onClick={onRetry}>Try again</Button>
      </div>
    </Card>
  );
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <Card>
      <p className="text-[20px] font-medium text-ink">{title}</p>
      <p className="mt-2 text-[15px] text-mute">{body}</p>
    </Card>
  );
}

export function Heading({ title, kicker }: { title: string; kicker?: string }) {
  return (
    <header className="mb-8">
      {kicker ? <p className="mb-2 text-[13px] tracking-wide text-mute">{kicker}</p> : null}
      <h1 className="text-[32px] font-semibold leading-tight text-ink md:text-[40px]">{title}</h1>
    </header>
  );
}
