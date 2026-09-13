"use client";

import clsx from "clsx";
import {
  InputHTMLAttributes,
  SelectHTMLAttributes,
  TextareaHTMLAttributes,
  forwardRef,
} from "react";

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={clsx(
        "focus-ring w-full rounded-lg border border-borderLight bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={clsx(
        "focus-ring w-full resize-y rounded-lg border border-borderLight bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted",
        className
      )}
      {...props}
    />
  )
);
Textarea.displayName = "Textarea";

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement>>(
  ({ className, children, ...props }, ref) => (
    <select
      ref={ref}
      className={clsx(
        "focus-ring w-full rounded-lg border border-borderLight bg-surface px-3 py-2 text-sm text-ink",
        className
      )}
      {...props}
    >
      {children}
    </select>
  )
);
Select.displayName = "Select";

export function Switch({
  checked,
  onChange,
  disabled,
  label,
}: {
  checked: boolean;
  onChange: () => void;
  disabled?: boolean;
  label?: string;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      disabled={disabled}
      onClick={onChange}
      className={clsx(
        "focus-ring relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors disabled:opacity-40",
        checked ? "bg-success" : "bg-borderLight"
      )}
    >
      <span
        className={clsx(
          "inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform",
          checked ? "translate-x-4.5" : "translate-x-1"
        )}
        style={{ transform: checked ? "translateX(18px)" : "translateX(4px)" }}
      />
    </button>
  );
}

const badgeStyles: Record<string, string> = {
  success: "bg-success/10 text-success border-success/30",
  danger: "bg-danger/10 text-danger border-danger/30",
  warning: "bg-warning/10 text-warning border-warning/30",
  muted: "bg-white/5 text-muted border-borderLight",
  accent: "bg-accent/10 text-accent border-accent/30",
};

export function Badge({
  tone = "muted",
  children,
  className,
}: {
  tone?: keyof typeof badgeStyles;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium",
        badgeStyles[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
